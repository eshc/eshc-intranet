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
    response_count = models.IntegerField(verbose_name='Number of responses', default=0)
    class Meta:
        ordering = ('-census_name',)

    def census_url(self):
        try:
            surl = urls.reverse('census:census-form', kwargs={'session_id': self.id})
            return 'https://%s%s' % (Site.objects.get_current().domain, surl)
        except:
            return 'Save me first'
    census_url.short_description = 'Census form URL (web address)'

    def census_response_url(self):
        try:
            surl = urls.reverse('census:census-results', kwargs={'session_id': self.id})
            return 'https://%s%s' % (Site.objects.get_current().domain, surl)
        except:
            return 'Save me first'
    census_url.short_description = 'Census result URL (web address)'

    def __str__(self):
        return ('Census %s' % (self.census_name)).strip()

    def is_census_open(self):
        return self.open_time <= now() <= self.close_time
    is_census_open.boolean = True

    def questions(self):
        return CensusQuestion.objects.filter(session=self).order_by('order')


class QuestionType(Enum):
    LongText = "Long Text"
    ShortText = "Short Text"
    SingleChoice = "Single Choice"
    MultipleChoice = "Multiple Choice"


class CensusQuestion(OrderedModel):
    order_with_respect_to = 'session'

    class Meta(OrderedModel.Meta):
        pass

    session = models.ForeignKey(CensusSession, on_delete=CASCADE)
    visible_in_voting = models.BooleanField(verbose_name='Visible for voters', default=True)
    question_text = models.TextField(verbose_name='Question text', max_length=5000)
    question_type = models.CharField(verbose_name='Type', max_length=20,
                                     choices=[(tag.name, tag.value) for tag in QuestionType],
                                     default=QuestionType.LongText)
    question_options = models.TextField(verbose_name='Question options (optional)', max_length=300, blank=True)
    required = models.BooleanField(verbose_name='Required', default=True)

    def __str__(self):
        return self.question_text

    def options_array(self):
        return self.question_options.splitlines(False)
    
    def responses(self):
        return CensusResponse.objects.filter(session=self.session, question=self)
    
    # @staticmethod
    def get_aggregated_responses(self):
        answers = []
        for key in range(len(self.options_array())):
            answers.append((self.options_array()[key], CensusResponse.objects.filter(session=self.session, question=self, answer_choice=key).count()))
        return answers


class CensusResponse(models.Model):
    session = models.ForeignKey(CensusSession, on_delete=CASCADE, verbose_name='Census session')
    question = models.ForeignKey(CensusQuestion, on_delete=CASCADE)

    answer_text = models.TextField(max_length=500000, blank=True, null=True)
    answer_choice = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.question.question_text[:15], self.get_answer_display())

    def get_answer_display(self):
        if self.question.question_type == QuestionType.LongText or self.question.question_type  == QuestionType.ShortText:
            return self.answer_text
        elif self.question.question_type == QuestionType.SingleChoice or self.question.question_type == QuestionType.MultipleChoice:
            return ', '.join([str(choice) for choice in self.answer_choice.all()])
        return ''

    class Meta:
        ordering = ('session',)