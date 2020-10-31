from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from polls.models import Question, Choice

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class VotingTest(TestCase) :
    

    def setUp(self):
        user = User.objects.create_user("Firstykus44", email="tsorawichaya@gmail.com", password="abcdef")
        user.first_name = 'Chopper'
        user.last_name = 'Tony Tony'
        user.save()
        self.client.login(username="Firstykus44", password="abcdef")

    def test_unauthenticated_vote(self):
        question = create_question(question_text="Sample test", days=-1)
        response = self.client.get(reverse("polls:vote", args=(question.id,)))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_vote(self):
        self.client.login(username="Firstykus44", password="abcdef")
        question = create_question(question_text="Sample test 2", days=-1)
        response = self.client.get(reverse("polls:vote", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
