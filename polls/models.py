import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """The question of the poll."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date ended', default=timezone.now() + datetime.timedelta(days=1))
    last_vote = models.CharField(max_length=200, default="")
    now = timezone.now()

    def __str__(self):
        """Return the qusetion text."""
        return self.question_text

    def was_published_recently(self):
        """The question is published recently."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """The qusetion is published or not."""
        now = timezone.now()
        return self.pub_date <= now

    def can_vote(self):
        """The question could vote or not."""
        now = timezone.now()
        return self.pub_date <= now <= self.end_date

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    """Choice of the questions."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Return the choice text."""
        return self.choice_text


class Vote(models.Model):
    "Vote the choice of questions."

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
