from django.contrib import admin
from django.db.models import Sum
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

from .models import ApplicationSession, ApplicationQuestion, Applicant, ApplicationAnswer, ApplicationVote


class QuestionsAdmin(OrderedTabularInline):
    model = ApplicationQuestion
    ordering = ('order',)
    fields = ('question_text', 'question_type', 'question_options', 'order', 'move_up_down_links')
    readonly_fields = ('order', 'move_up_down_links')
    extra = 0


@admin.register(ApplicationSession)
class ApplicationAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'move_in_date', 'open_time', 'close_time', 'voting_close_time')
    save_as = True
    inlines = (QuestionsAdmin,)


class ApplicantQuestionsInline(admin.StackedInline):
    model = ApplicationAnswer
    extra = 0


@admin.register(Applicant)
class ApplicantViewAdmin(admin.ModelAdmin):

    def vote_stats(self, applicant: Applicant) -> str:
        count = ApplicationVote.objects.filter(applicant=applicant).count()
        pos = ApplicationVote.objects.filter(applicant=applicant, points__gte=0).aggregate(Sum('points'))['points__sum'] or 0
        neg = ApplicationVote.objects.filter(applicant=applicant, points__lt=0).aggregate(Sum('points'))['points__sum'] or 0

        return '%d votes, score: %d (+%d,-%d)' % (count, pos+neg, pos, -neg)

    list_display = ('session', '__str__', 'email', 'phone_number',
                    'is_past_applicant', 'verified_past_applicant', 'vote_count', 'vote_stats')
    list_filter = ('session', 'is_past_applicant')
    readonly_fields = ('date_applied',)
    inlines = (ApplicantQuestionsInline,)
