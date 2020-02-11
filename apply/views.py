import traceback
from collections import OrderedDict
from typing import Union

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponseServerError
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from . import models
import re
import sys

data_re = re.compile('[ a-zA-Z0-9@.+]*')


def active_member_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.profile.current_member,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class ApplyView(TemplateView):
    template_name = 'apply/apply.html'
    success_template_name = 'apply/success.html'

    def post(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        app_session: models.ApplicationSession = get_object_or_404(models.ApplicationSession, pk=kwargs['session_id'])
        if not app_session.is_applying_open():
            return self.get(request, *args, **kwargs)

        questions = app_session.questions()
        simple_fields = [
            'first_name', 'last_name', 'preferred_name',
            'email', 'phone_number'
        ]
        data = dict()
        data['answers'] = OrderedDict()
        mistakes = []
        data['is_past_applicant'] = (request.POST.get('is_past_applicant', '') == 'on')
        data['confidential_note'] = str(request.POST.get('confidential_note', ''))
        for f in simple_fields:
            rqdata: str = request.POST.get(f, '')
            if re.fullmatch(data_re, rqdata) is None:
                data[f] = ''
                mistakes.append(f)
                continue
            data[f] = rqdata
        for q in questions:
            qname = 'question_%d' % (q.pk,)
            if q.question_type == models.QuestionType.MultipleChoice.name:
                data['answers'][q.pk] = request.POST.getlist(qname, [])
            else:
                data['answers'][q.pk] = request.POST.getlist(qname, [''])[0]

        if models.Applicant.objects.filter(session=app_session, email=data['email']).count() > 0:
            mistakes.append(
                'Sorry, but an application with this e-mail address already exists. Please contact us on our main e-mail to change your application details.')

        if len(mistakes) == 0:
            # Add application and send e-mail
            try:
                ap = models.Applicant.objects.create(
                    session=app_session,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    preferred_name=data['preferred_name'],
                    email=data['email'],
                    phone_number=data['phone_number'],
                    is_past_applicant=data['is_past_applicant'],
                    verified_past_applicant=False,
                    confidential_note=data['confidential_note'],
                    app_team_note='unprocessed',
                    date_applied=models.now())
                for qpk, qans in data['answers'].items():
                    ans = qans
                    if type(ans) == list:
                        ans = ', '.join(ans)
                    models.ApplicationAnswer.objects.create(
                        applicant=ap,
                        question_id=qpk,
                        answer=ans)
                ap.refresh_from_db()
            except:
                mistakes.append('Could not put application in the database: ' + sys.exc_info()[0])
            else:
                msg = """Dear %s,

Your application to the Edinburgh Student Housing Co-operative has been received and will soon be reviewed.
Here are the answers you provided to our questions provided for your reference:
""" % (ap.get_introduction_name(),)
                for field in models.Applicant._meta.get_fields():
                    fn = field.name
                    vn = getattr(field, 'verbose_name', '')
                    if len(vn) < 1:
                        continue
                    if fn != 'verified_past_applicant' and fn != 'answers' and fn != 'app_team_note':
                        msg += '\n%s: %s' % (vn, str(getattr(ap, fn, '')))
                for q in questions:
                    ans = models.ApplicationAnswer.objects.get(applicant=ap, question=q).answer
                    msg += '\n\n%s: %s' % (q.question_text, ans)

                msg += '\n\nKind regards,\nEdinburgh Student Housing Co-operative Applications Team'
                mail = EmailMessage(
                    subject='Your application has been received',
                    body=msg,
                    from_email='intranet@eshc.coop',
                    to=[ap.email],
                    reply_to=['applications@eshc.coop']
                )
                mail.send(fail_silently=True)

        for k, v in data.items():
            ctx[k] = v
        ctx['num_mistakes'] = len(mistakes)
        if len(mistakes) > 0:
            ctx['error_message'] = 'Please correct some of your answers below. Mistakes in fields: ' + ', '.join(
                mistakes)
            return self.render_to_response(ctx)
        else:
            return render_to_response(self.success_template_name, ctx, self.content_type)

    def get_context_data(self, **kwargs) -> dict:
        app_session: models.ApplicationSession = get_object_or_404(models.ApplicationSession, pk=kwargs['session_id'])
        ctx = {
            'session': app_session
        }
        return ctx


def find_applicant(app_session: models.ApplicationSession, member: User) -> Union[models.Applicant, None]:
    applicants = models.Applicant.objects.filter(session=app_session).order_by('vote_count')
    for ap in applicants:
        if ap.applicationvote_set.filter(voting_member=member).count() == 0:
            return ap
    return None


def get_answers(applicant: models.Applicant):
    qs = applicant.session.questions().filter(visible_in_voting=True)
    ans = dict()
    for q in qs:
        try:
            a: models.ApplicationAnswer = models.ApplicationAnswer.objects.get(applicant=applicant, question=q)
            if q.question_type == models.QuestionType.ShortText.name:
                ans[q.pk] = a.answer
            elif q.question_type == models.QuestionType.LongText.name:
                ans[q.pk] = a.answer
            elif q.question_type == models.QuestionType.SingleChoice.name:
                ans[q.pk] = a.answer
            elif q.question_type == models.QuestionType.MultipleChoice.name:
                ans[q.pk] = [s.strip() for s in a.answer.split(', ')]
            else:
                ans[q.pk] = 'system error'
        except models.ApplicationAnswer.DoesNotExist:
            ans[q.pk] = 'Applicant did not provide an answer to this question.'
    return ans


class VoteView(TemplateView):
    template_name = "apply/vote.html"

    def get_context_data(self, **kwargs) -> dict:
        app_session: models.ApplicationSession = get_object_or_404(models.ApplicationSession, pk=kwargs['session_id'])

        ctx = {
            'session': app_session
        }
        return ctx

    @method_decorator(active_member_required)
    def get(self, request: HttpRequest, *args, **kwargs):
        try:
            ctx = self.get_context_data(**kwargs)
            session = ctx['session']
            if session.is_voting_open:
                member: User = request.user
                next_applicant: models.Applicant = find_applicant(ctx['session'], member)
                ctx['applicant'] = next_applicant
                if next_applicant:
                    ctx['answers'] = get_answers(next_applicant)
            resp = self.render_to_response(ctx)
            return resp
        except Exception as e:
            msg = traceback.format_exc()
            mail = EmailMessage(subject='Intranet application voting error traceback',
                    body=msg,
                    from_email='intranet@eshc.coop',
                    to=['intranet-notify@lists.eshc.coop'])
            mail.send(True)
            return HttpResponseServerError('Sorry, server error occured')


    @method_decorator(active_member_required)
    def post(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        session = ctx['session']
        if not session.is_voting_open:
            ctx['error_message'] = "Voting for this application session is now closed!"
            return self.render_to_response(ctx)
        member: User = request.user
        applicant: models.Applicant = models.Applicant.objects.get(pk=int(request.POST.get('applicant')))
        if applicant.session != session:
            ctx['error_message'] = "Invalid request!"
            return self.render_to_response(ctx)
        if models.ApplicationVote.objects.filter(applicant=applicant, voting_member=member).count() != 0:
            ctx['error_message'] = "You have already voted for applicant #%d!" % (applicant.pk,)
            return self.render_to_response(ctx)
        vote_str = str(request.POST.get('voteValue')).upper()
        vote = -999
        if vote_str == "NOTSUITABLE":
            vote = -2
        elif vote_str == "SUITABLE":
            vote = 1
        elif vote_str == "EXCEPTIONAL":
            vote = 2
        elif vote_str == "ABSTAIN":
            vote = 0
        if vote == -999:
            ctx['error_message'] = "Invalid voting option %s!" % (vote_str,)
            return self.render_to_response(ctx)
        # register vote
        models.ApplicationVote.objects.create(
            voting_member=member,
            applicant=applicant,
            points=vote
        )
        applicant.vote_count += 1
        applicant.save()
        ctx['succ_message'] = "You have voted for applicant #%d!" % (applicant.pk,)
        next_applicant: models.Applicant = find_applicant(ctx['session'], member)
        ctx['applicant'] = next_applicant
        if next_applicant:
            ctx['answers'] = get_answers(next_applicant)
        return self.render_to_response(ctx)
