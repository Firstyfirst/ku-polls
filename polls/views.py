from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Vote
from datetime import datetime
import logging

log = logging.getLogger("ku-polls")
logging.basicConfig(level=logging.INFO)

def get_client_ip(request):
    """Get the client's ip address."""

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR')

@receiver(user_logged_in)
def update_choice_login(request, **kwargs):
    """Update the last vote after user login."""
    
    for question in Question.objects.all():
        question.last_vote = str(request.user.vote_set.get(question=question).selected_choice)
        question.save()

@receiver(user_logged_in)
def log_user_logged_in(sender, request, user, **kwargs):
    
    """Logging after user login."""
    log.info(f'Login user: {user} , IP: {get_client_ip(request)} , Date: {datetime.now()}')


@receiver(user_logged_out)
def log_user_logged_out(sender, request, user, **kwargs):
    """Logging after user logout."""
    
    log.info(f'Logout user: {user} , IP: {get_client_ip(request)} , Date: {datetime.now()}')


@receiver(user_login_failed)
def log_user_login_failed(sender, request, credentials, **kwargs):
    """Logging when user fail to login."""
    
    log.warning('Login user(failed): %s , IP: %s , Date: %s', credentials['username'], get_client_ip(request), str(datetime.now()))

class IndexView(generic.ListView):
    """Show all activated question."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')


class DetailView(generic.DetailView):
    """Show the choice of the question in that page."""

    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, **kwargs):
        """The method of HTTP."""
        try:
            question = Question.objects.get(pk=kwargs['pk'])
            if not question.can_vote():
                return HttpResponseRedirect(reverse('polls:index'), messages.error(request, "This poll has been out of date."))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(reverse('polls:index'), messages.error(request, "Poll does not exist."))
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(object=self.get_object()))

    def get_queryset(self):
        """Excludes any questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """Show the result page."""

    model = Question
    template_name = 'polls/results.html'

@login_required()
def vote(request, question_id):
    """Make the voting and redirection to result page."""
    
    user = request.user
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        return HttpResponseRedirect(reverse('polls:index'), messages.error(request, "This poll has been out of date."))
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        Vote.objects.update_or_create(user=user, question=question, defaults={'selected_choice': selected_choice})
        for choice in question.choice_set.all():
            choice.votes = Vote.objects.filter(question=question).filter(selected_choice=choice).count()
            choice.save()
        for question in Question.objects.all():
            question.last_vote = str(request.user.vote_set.get(question=question).selected_choice)
            question.save()
        date = datetime.now()
        log = logging.getLogger("polls")
        log.info("User: %s, Poll's ID: %d, Date: %s.", user, question_id, str(date))
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
