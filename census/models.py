from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db.models import CASCADE
from ordered_model.models import OrderedModel
from enum import Enum
from django.utils import timezone
from django import urls


def now():
    return timezone.now()


class CensusSession(models.Model):
    census_name = models.TextField(verbose_name='Census name (e.g. 2024 Semester 1)')
    open_time = models.DateTimeField(verbose_name='Census form opening time')
    close_time = models.DateTimeField(verbose_name='Census form closing time')
    class Meta:
        ordering = ('-census_name',)

    def apply_url(self):
        try:
            surl = urls.reverse('census:census-form', kwargs={'session_id': self.id})
            return 'https://%s%s' % (Site.objects.get_current().domain, surl)
        except:
            return 'Save me first'
    apply_url.short_description = 'Census form URL (web address)'

    def __str__(self):
        return ('Census %s' % (self.census_name)).strip()

    def is_census_open(self):
        return self.open_time <= now() <= self.close_time
    is_census_open.boolean = True

    def questions(self):
        return CensusQuestion.objects.filter(session=self).order_by('order')


class QuestionType(Enum):
    LongText = "Long Text"
    ShortText = "One Line Text"
    SingleChoice = "Single Choice"
    MultipleChoice = "Multiple Choice"


class CensusQuestion(OrderedModel):
    order_with_respect_to = 'session'

    class Meta(OrderedModel.Meta):
        pass

    session = models.ForeignKey(CensusSession, on_delete=CASCADE)
    visible_in_voting = models.BooleanField(verbose_name='Visible for voters', default=True)
    question_text = models.CharField(verbose_name='Question text', max_length=500)
    question_type = models.CharField(verbose_name='Type', max_length=20,
                                     choices=[(tag.name, tag.value) for tag in QuestionType],
                                     default=QuestionType.LongText)
    question_options = models.TextField(verbose_name='Question options (optional)', max_length=300, blank=True)

    def __str__(self):
        return self.question_text

    def options_array(self):
        return self.question_options.splitlines(False)


class CensusResponse(models.Model):
    session = models.ForeignKey(CensusSession, on_delete=CASCADE, verbose_name='Census session')
    # TODO: ADD QUESTIONS

    # first_name = models.CharField(verbose_name='First name', max_length=30)
    # last_name = models.CharField(verbose_name='Last name', max_length=150)
    # preferred_name = models.CharField(verbose_name='Preferred name', max_length=30, blank=True)
    # email = models.EmailField(verbose_name='Email address')
    # phone_number = models.CharField(verbose_name='Phone number', max_length=15, blank=True)
    # is_past_applicant = models.BooleanField(verbose_name='Past applicant', default=False)
    # verified_past_applicant = models.BooleanField(verbose_name='Verified past applicant', default=False)
    # confidential_note = models.TextField(verbose_name='Confidential information', max_length=1000, blank=True)
    # app_team_note = models.TextField(verbose_name='Applications team notes (invisible to applicant)', max_length=1000,
    #                                  blank=True)
    # date_applied = models.DateTimeField(verbose_name='Date applied', auto_now_add=True)
    # answers = models.ManyToManyField(ApplicationQuestion, through='ApplicationAnswer', blank=True)
    # vote_count = models.IntegerField(verbose_name='Votes received', default=0)

    class Meta:
        ordering = ('session__move_in_date', 'last_name', 'first_name')

    def __str__(self):
        return ('Census %s' % (self.census_name)).strip()
        
class CensusIndividualResponse(models.Model):
    session = models.ForeignKey(CensusSession, on_delete=CASCADE, verbose_name='Census session')
    # TODO: ADD QUESTIONS
    
    # first_name = models.CharField(verbose_name='First name', max_length=30)
    # last_name = models.CharField(verbose_name='Last name', max_length=150)
    # preferred_name = models.CharField(verbose_name='Preferred name', max_length=30, blank=True)
    # email = models.EmailField(verbose_name='Email address')
    # phone_number = models.CharField(verbose_name='Phone number', max_length=15, blank=True)
    # is_past_applicant = models.BooleanField(verbose_name='Past applicant', default=False)
    # verified_past_applicant = models.BooleanField(verbose_name='Verified past applicant', default=False)
    # confidential_note = models.TextField(verbose_name='Confidential information', max_length=1000, blank=True)
    # app_team_note = models.TextField(verbose_name='Applications team notes (invisible to applicant)', max_length=1000,
    #                                  blank=True)
    # date_applied = models.DateTimeField(verbose_name='Date applied', auto_now_add=True)
    # answers = models.ManyToManyField(ApplicationQuestion, through='ApplicationAnswer', blank=True)
    # vote_count = models.IntegerField(verbose_name='Votes received', default=0)

    class Meta:
        ordering = ('session__move_in_date', 'last_name', 'first_name')

    def __str__(self):
        if self.preferred_name:
            return '%s (%s %s)' % (self.preferred_name, self.first_name, self.last_name)
        else:
            return '%s %s' % (self.first_name, self.last_name)

    def get_introduction_name(self):
        if self.preferred_name:
            return self.preferred_name
        else:
            return self.first_name


class ApplicationAnswer(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=CASCADE)
    question = models.ForeignKey(ApplicationQuestion, on_delete=CASCADE)
    answer = models.TextField(max_length=5000)

    def __str__(self):
        return '%s: %s' % (self.question.question_text[:15], self.answer[:50])

