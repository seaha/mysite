from django.test import TestCase
from django.utils import timezone
import datetime

from .models import Question

# Create your tests here.
class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_quesion = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)