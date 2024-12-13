import csv
from typing import List

from django.contrib import admin, messages
from django.db.models import Sum, QuerySet, Field
from django.http import HttpRequest, HttpResponse
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

from .models import CensusSession, CensusQuestion, CensusResponse


class CensusQuestionsAdmin(OrderedTabularInline):
    model = CensusQuestion
    ordering = ('order',)
    fields = ('question_text', 'question_type', 'required', 'question_options', 'order', 'move_up_down_links')
    readonly_fields = ('order', 'move_up_down_links')
    extra = 0

class CensusResponsesAdmin(OrderedTabularInline):
    model = CensusResponse
    # ordering = ('order',)
    fields = ('question', )
    readonly_fields = ('question', 'answer_text', 'answer_choice')
    extra = 0


@admin.register(CensusSession)
class CensusAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'census_name',
                    'is_census_open',
                    'open_time', 'close_time')
    save_as = True
    inlines = (CensusQuestionsAdmin,)
    actions = ['export_responses']
    readonly_fields = ('response_count', 'census_url', 'census_response_url')

    def export_responses(self, request: HttpRequest, queryset: QuerySet):
        if queryset.count() != 1:
            self.message_user(request, "Please select only one session for export", messages.ERROR)
            return
        session: CensusSession = queryset.get()
        csv_resp = HttpResponse(content_type='text/csv')
        csv_resp['Content-Disposition'] = 'attachment; filename="%s.csv"' % (session,)
        wr = csv.writer(csv_resp)
        for q in session.questions():
            wr.writerow([q.question_text])
            if q.question_type == "LongText" or q.question_type == "ShortText":
                answers = []
                for r in CensusResponse.objects.filter(question=q, session=session).order_by('?'):
                    answers.append(r.answer_text)
                wr.writerow(answers)
            if q.question_type == 'SingleChoice' or q.question_type == 'MultipleChoice':
                options = []
                counts = []
                for response in q.get_aggregated_responses():
                    options.append(response[0])
                    counts.append(response[1])
                wr.writerow(options)
                wr.writerow(counts)
                
        return csv_resp

    export_responses.short_description = "Export census data to a spreadsheet file"


# TODO
# @admin.register(Applicant)
# class ApplicantViewAdmin(admin.ModelAdmin):

#     def vote_stats(self, applicant: Applicant) -> str:
#         count = ApplicationVote.objects.filter(applicant=applicant).count()
#         pos = ApplicationVote.objects.filter(applicant=applicant, points__gte=0).aggregate(Sum('points'))[
#                   'points__sum'] or 0
#         neg = ApplicationVote.objects.filter(applicant=applicant, points__lt=0).aggregate(Sum('points'))[
#                   'points__sum'] or 0
#         abstain = ApplicationVote.objects.filter(applicant=applicant, points__exact=0).aggregate(Sum('points'))[
#                   'points__sum'] or 0

#         return '%d votes, score: %d (+%d,-%d,abs%d)' % (count, pos + neg, pos, -neg, abstain)
#     vote_stats.short_description = 'Vote stats'

#     list_display = ('session', '__str__', 'email', 'phone_number',
#                     'is_past_applicant', 'verified_past_applicant', 'vote_count', 'vote_stats')
#     list_filter = ('session', 'is_past_applicant')
#     readonly_fields = ('date_applied', )
#     inlines = (ApplicantQuestionsInline,)
