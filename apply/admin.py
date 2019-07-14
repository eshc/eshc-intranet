from django.contrib import admin
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

from .models import ApplicationSession, ApplicationQuestion, Applicant, ApplicationAnswer


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
    list_filter = ('session', 'is_past_applicant')
    readonly_fields = ('date_applied',)
    inlines = (ApplicantQuestionsInline,)
