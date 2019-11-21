import csv
from typing import List

from django.contrib import admin, messages
from django.db.models import Sum, QuerySet, Field
from django.http import HttpRequest, HttpResponse
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
    list_display = ('__str__', 'applicant_count', 'votes_count', 'move_in_date',
                    'is_applying_open', 'is_voting_open',
                    'open_time', 'close_time', 'voting_close_time')
    save_as = True
    inlines = (QuestionsAdmin,)
    actions = ['export_applicants']
    readonly_fields = ('apply_url', 'vote_url')

    def applicant_count(self, session: ApplicationSession):
        return Applicant.objects.filter(session=session).count()

    def votes_count(self, session: ApplicationSession):
        return ApplicationVote.objects.filter(applicant__session=session).count()

    def export_applicants(self, request: HttpRequest, queryset: QuerySet):
        if queryset.count() != 1:
            self.message_user(request, "Please select only one session for export", messages.ERROR)
            return
        session: ApplicationSession = queryset.get()
        csv_resp = HttpResponse(content_type='text/csv')
        csv_resp['Content-Disposition'] = 'attachment; filename="Applicants %s.csv"' % (session.move_in_str(),)
        wr = csv.writer(csv_resp)
        fields: List[Field] = Applicant._meta.get_fields(include_parents=False, include_hidden=False)
        header = []
        fnames = []
        for f in fields:
            if f.is_relation:
                continue
            header.append(f.verbose_name)
            fnames.append(f.name)
        header.append("Abstain votes")
        header.append("Not suitable votes") # -2
        header.append("Suitable votes") # 1
        header.append("Very suitable votes") # 2
        qs = session.questions()
        for q in qs:
            header.append(q.question_text)
        wr.writerow(header)
        for ap in Applicant.objects.filter(session=session):
            row = []
            for f in fnames:
                row.append(getattr(ap, f))
            for vv in [0, -2, 1, 2]:
                vc = ApplicationVote.objects.filter(applicant=ap, points__exact=vv).count()
                row.append(vc)
            for q in qs:
                ans = 'no answer'
                try:
                    ans = ApplicationAnswer.objects.get(applicant=ap, question=q).answer
                except:
                    pass
                row.append(ans)
            wr.writerow(row)
        return csv_resp

    export_applicants.short_description = "Export applicants and vote stats to a spreadsheet file"


class ApplicantQuestionsInline(admin.StackedInline):
    model = ApplicationAnswer
    extra = 0


@admin.register(Applicant)
class ApplicantViewAdmin(admin.ModelAdmin):

    def vote_stats(self, applicant: Applicant) -> str:
        count = ApplicationVote.objects.filter(applicant=applicant).count()
        pos = ApplicationVote.objects.filter(applicant=applicant, points__gte=0).aggregate(Sum('points'))[
                  'points__sum'] or 0
        neg = ApplicationVote.objects.filter(applicant=applicant, points__lt=0).aggregate(Sum('points'))[
                  'points__sum'] or 0
        abstain = ApplicationVote.objects.filter(applicant=applicant, points__eq=0).aggregate(Sum('points'))[
                  'points__sum'] or 0

        return '%d votes, score: %d (+%d,-%d,abs%d)' % (count, pos + neg, pos, -neg, abstain)

    list_display = ('session', '__str__', 'email', 'phone_number',
                    'is_past_applicant', 'verified_past_applicant', 'vote_count', 'vote_stats')
    list_filter = ('session', 'is_past_applicant')
    readonly_fields = ('date_applied',)
    inlines = (ApplicantQuestionsInline,)
