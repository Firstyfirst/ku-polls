from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import Choice, Question


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


def vote(request, question_id):
    """Make the voting and redirection to result page."""
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
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
