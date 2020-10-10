import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):
    """Test model of the question in the different conditions."""

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    """Test the templete of index page for different type of questions."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    """Test the templete view for future question and past question."""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(
            question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(
            question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class IsPublishedTests(TestCase):
    """Test the question is published in the different time periods."""

    def test_is_published_before_pub_date(self):
        """The question is not published before pub date."""
        now = timezone.now
        self.assertTrue(now < Question.pub_date)
        self.assertFalse(Question.is_published())

    def test_is_published_on_date(self):
        """The question is published on pub date time."""
        now = timezone.now
        self.assertTrue(now >= Question.pub_date)
        self.assertTrue(now <= Question.end_date)
        self.assertTrue(Question.is_published())

    def test_is_published_after_pub_date(self):
        """The question is not published after pub date."""
        now = timezone.now
        self.assertTrue(now > Question.end_date)
        self.assertFalse(Question.is_published())


class CanVoteTest(TestCase):
    """Test all condition voting that could happen while the user use the application."""

    def test_can_vote_before_pub_date(self):
        """The user could not vote before pub date."""
        now = timezone.now
        self.assertTrue(now < Question.pub_date)
        self.assertFalse(Question.is_published())
        self.assertFalse(Question.can_vote())

    def test_can_vote(self):
        """The user could vote between pub date and end date interval."""
        now = timezone.now
        self.assertTrue(now >= Question.pub_date)
        self.assertTrue(now <= Question.end_date)
        self.assertTrue(Question.is_published())
        self.assertTrue(Question.can_vote())

    def test_can_vote_after_end_date(self):
        """The user could not vote after end date."""
        now = timezone.now
        self.assertTrue(now > Question.end_date)
        self.assertFalse(Question.is_published())
        self.assertFalse(Question.can_vote())

    # def setUp(self):
    #     self.client = Client()

    # def test_poll_index(self):
    #     pub_time = timezone.now() - datetime.timedelta(days=2)
    #     end_time = timezone.now() - datetime.timedelta(days=1)
    #     question = Question(question_text="This is sample ",pub_date=pub_time,end_date=end_time)
    #     question.save()
    #     respone = self.client.get(reverse('polls:index'))
    #     self.assertEqual(respone.status_code,200)
    #     self.assertContains(respone,"This is sample ")

    # def test_polls_index(self):
    #     pub_time = timezone.now() - datetime.timedelta(days=1)
    #     question = Question(question_text="ABCDEFGHIJ",pub_date=pub_time)
    #     question.save()
    #     response = self.client.get('/polls/')
    #     self.assertTemplateUsed(response,template_name='polls/index.html')
    #     # Is test poll included in the page?
    #     self.assertContains(response,"ABCDEFGHIJ")

    # def get_vote(self):
    #     response =self.client.post('/polls/1/', {'choice': '2'})
