from django.test import TestCase
from django.utils import timezone
from datetime import datetime
from polls.models import Question


class IsPublishedTests(TestCase):
    """Test the question is published in the different time periods."""

    def test_is_published_before_pub_date(self):
        """The question is not published before pub date."""
        now = timezone.now()
        question = Question("Test1", pub_date=now + datetime.timedelta(days=1))
        self.assertTrue(now < question.pub_date)
        self.assertFalse(question.is_published())

    def test_is_published_on_date(self):
        """The question is published on pub date time."""
        now = timezone.now()
        question = Question("Test1", pub_date=now - datetime.timedelta(days=1), end_date=now + datetime.timedelta(days=3))
        self.assertTrue(now >= question.pub_date)
        self.assertTrue(now <= question.end_date)
        self.assertTrue(question.is_published())

    def test_is_published_after_pub_date(self):
        """The question is not published after pub date."""
        now = timezone.now()
        question = Question("Test1", pub_date=now - datetime.timedelta(days=2), end_date=now - datetime.timedelta(days=1))
        self.assertTrue(now > question.end_date)
        self.assertTrue(question.is_published())


class CanVoteTest(TestCase):
    """Test all condition voting that could happen while the user use the application."""

    def test_can_vote_before_pub_date(self):
        """The user could not vote before pub date."""
        now = timezone.now()
        question = Question("Test1", pub_date=now + datetime.timedelta(days=1))
        self.assertTrue(now < question.pub_date)
        self.assertFalse(question.is_published())
        self.assertFalse(question.can_vote())

    def test_can_vote(self):
        """The user could vote between pub date and end date interval."""
        now = timezone.now()
        question = Question("Test1", pub_date=now - datetime.timedelta(days=1), end_date=now + datetime.timedelta(days=3))
        self.assertTrue(now >= question.pub_date)
        self.assertTrue(now <= question.end_date)
        self.assertTrue(question.is_published())
        self.assertTrue(question.can_vote())

    def test_can_vote_after_end_date(self):
        """The user could not vote after end date."""
        now = timezone.now()
        question = Question("Test1", pub_date=now - datetime.timedelta(days=2), end_date=now - datetime.timedelta(days=1))
        self.assertTrue(now > question.end_date)
        self.assertTrue(question.is_published())
        self.assertFalse(question.can_vote())
