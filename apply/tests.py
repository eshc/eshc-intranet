import datetime
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.test import TestCase

# Create your tests here.
from .models import ApplicationSession, ApplicationQuestion

class ApplicationSessionTests(TestCase):
    def test_is_today_application_open(self):
        startdate = timezone.now()
        enddate = timezone.now() + datetime.timedelta(days=30)
        session = ApplicationSession(move_in_date=enddate, open_time=startdate, close_time=enddate,voting_open_time=enddate,voting_close_time=enddate)
        self.assertIs(session.is_applying_open(),True)


class ApplicationQuestionTests(TestCase):

    def test_is_question_correct_length(self):
        startdate = timezone.now()
        enddate = timezone.now() + datetime.timedelta(days=30)
        session = ApplicationSession(move_in_date=enddate, open_time=startdate, close_time=enddate,voting_open_time=enddate,voting_close_time=enddate)
        long_enough_title = get_random_string(500) 
        long_enough_question  = ApplicationQuestion(session=session,question_text=long_enough_title)
        self.assertEqual(len(long_enough_question.question_text),500)

