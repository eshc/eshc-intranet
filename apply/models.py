from django.db import models
from django.contrib.auth.models import User
from django.db.models import CASCADE
from ordered_model.models import OrderedModel
from enum import Enum


class ApplicationSession(models.Model):

    special_title = models.CharField(verbose_name='Special name, e.g. Summerletter', max_length=30, blank=True)
    move_in_date = models.DateField(verbose_name='Move-in date')
    open_time = models.DateTimeField(verbose_name='Applications form opening time')
    close_time = models.DateTimeField(verbose_name='Applications form closing time, Voting opening time')
    voting_close_time = models.DateTimeField(verbose_name='Members voting closing time')

    class Meta:
        ordering = ('-move_in_date',)

    def move_in_str(self):
        """Converts move-in date to a string like: "September 2014"."""
        return self.move_in_date.strftime('%B %Y')

    def __str__(self):
        return ('%s %s move-in' % (self.special_title, self.move_in_str())).strip()


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
    question_text = models.CharField(verbose_name='Question text', max_length=300)
    question_type = models.CharField(verbose_name='Type', max_length=20,
                                     choices=[(tag.name, tag.value) for tag in QuestionType],
                                     default=QuestionType.LongText)
    question_options = models.TextField(verbose_name='Question options (optional)', max_length=300, blank=True)

    def __str__(self):
        return self.question_text


class Applicant(models.Model):

    session = models.ForeignKey(ApplicationSession, on_delete=CASCADE)
    first_name = models.CharField(verbose_name='First name', max_length=30)
    last_name = models.CharField(verbose_name='Last name', max_length=150)
    preferred_name = models.CharField(verbose_name='Preferred name', max_length=30, blank=True)
    email = models.EmailField(verbose_name='Email address')
    phone_number = models.CharField(max_length=15, blank=True)
    is_past_applicant = models.BooleanField(verbose_name='Past applicant', default=False)
    verified_past_applicant = models.BooleanField(verbose_name='Verified past applicant', default=False)
    date_applied = models.DateTimeField(verbose_name='Date applied', auto_now=True)
    answers = models.ManyToManyField(ApplicationQuestion, through='ApplicationAnswer')

    class Meta:
        ordering = ('session__move_in_date', 'last_name', 'first_name')

    def __str__(self):
        if self.preferred_name:
            return '%s (%s %s)' % (self.preferred_name, self.first_name, self.last_name)
        else:
            return '%s %s' % (self.first_name, self.last_name)


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
