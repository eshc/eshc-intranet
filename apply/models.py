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


class ApplicationSession(models.Model):
    special_title = models.CharField(verbose_name='Special name, e.g. Summerletter', max_length=30, blank=True)
    move_in_date = models.DateField(verbose_name='Move-in date')
    open_time = models.DateTimeField(verbose_name='Applications form opening time')
    close_time = models.DateTimeField(verbose_name='Applications form closing time')
    voting_open_time = models.DateTimeField(verbose_name='Members voting opening time')
    voting_close_time = models.DateTimeField(verbose_name='Members voting closing time')

    class Meta:
        ordering = ('-move_in_date',)

    def apply_url(self):
        try:
            surl = urls.reverse('apply:apply-form', kwargs={'session_id': self.id})
            return 'https://%s%s' % (Site.objects.get_current().domain, surl)
        except:
            return 'Save me first'
    apply_url.short_description = 'Application form URL (web address)'

    def vote_url(self):
        try:
            surl = urls.reverse('apply:vote-form', kwargs={'session_id': self.id})
            return 'https://%s%s' % (Site.objects.get_current().domain, surl)
        except:
            return 'Save me first'
    vote_url.short_description = 'Voting URL (web address)'

    def move_in_str(self):
        """Converts move-in date to a string like: "September 2014"."""
        return self.move_in_date.strftime('%B %Y')

    def __str__(self):
        return ('%s %s move-in' % (self.special_title, self.move_in_str())).strip()

    def is_applying_open(self):
        return self.open_time <= now() <= self.close_time
    is_applying_open.boolean = True

    def is_voting_open(self):
        return self.voting_open_time <= now() <= self.voting_close_time
    is_voting_open.boolean = True

    def questions(self):
        return ApplicationQuestion.objects.filter(session=self).order_by('order')

    def voting_questions(self):
        return self.questions().filter(visible_in_voting=True)


def voting_open_sessions():
    t = now()
    return ApplicationSession.objects.filter(
        voting_open_time__lte=t,
        voting_close_time__gte=t
    )


class QuestionType(Enum):
    LongText = "Long Text"
    ShortText = "One Line Text"
    SingleChoice = "Single Choice"
    MultipleChoice = "Multiple Choice"


class ApplicationQuestion(OrderedModel):
    order_with_respect_to = 'session'

    class Meta(OrderedModel.Meta):
        pass

    session = models.ForeignKey(ApplicationSession, on_delete=CASCADE)
    visible_in_voting = models.BooleanField(verbose_name='Visible for voters', default=True)
    question_text = models.CharField(verbose_name='Question text', max_length=5000)
    question_type = models.CharField(verbose_name='Type', max_length=20,
                                     choices=[(tag.name, tag.value) for tag in QuestionType],
                                     default=QuestionType.LongText)
    question_options = models.TextField(verbose_name='Question options (optional)', max_length=300, blank=True)

    def __str__(self):
        return self.question_text

    def options_array(self):
        return self.question_options.splitlines(False)


class Applicant(models.Model):
    session = models.ForeignKey(ApplicationSession, on_delete=CASCADE, verbose_name='Application session')
    first_name = models.CharField(verbose_name='First name', max_length=30)
    last_name = models.CharField(verbose_name='Last name', max_length=150)
    preferred_name = models.CharField(verbose_name='Preferred name', max_length=30, blank=True)
    email = models.EmailField(verbose_name='Email address')
    phone_number = models.CharField(verbose_name='Phone number', max_length=15, blank=True)
    is_past_applicant = models.BooleanField(verbose_name='Past applicant', default=False)
    verified_past_applicant = models.BooleanField(verbose_name='Verified past applicant', default=False)
    confidential_note = models.TextField(verbose_name='Confidential information', max_length=1000, blank=True)
    app_team_note = models.TextField(verbose_name='Applications team notes (invisible to applicant)', max_length=1000,
                                     blank=True)
    date_applied = models.DateTimeField(verbose_name='Date applied', auto_now_add=True)
    answers = models.ManyToManyField(ApplicationQuestion, through='ApplicationAnswer', blank=True)
    vote_count = models.IntegerField(verbose_name='Votes received', default=0)

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


class ApplicationVote(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=CASCADE)
    voting_member = models.ForeignKey(User, on_delete=CASCADE)
    points = models.IntegerField()
