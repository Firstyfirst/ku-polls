from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime
from polls.models import Question

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class AuthenticationTest(TestCase):
    

    def setUp(self):
        user = User.objects.create_user("Firstykus44", email="tsorawichaya@gmail.com", password="abcdef")
        user.first_name = 'Chopper'
        user.last_name = 'Tony Tony'
        user.save()

    def test_authenticated_user(self):
        self.client.login(username="Firstykus44", password="abcdef")
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Chopper")
        self.assertContains(response, "Tony Tony")

    def test_unauthenticated_user(self):
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Chopper")
        self.assertContains(response, "Tony Tony")
