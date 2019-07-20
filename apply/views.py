from collections import OrderedDict

from django.core.mail import EmailMessage
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import TemplateView

from . import models
import re
import sys

data_re = re.compile('[ a-zA-Z0-9@.+]*')


class ApplyView(TemplateView):
    template_name = 'apply/apply.html'
    success_template_name = 'apply/success.html'

    def post(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        app_session: models.ApplicationSession = get_object_or_404(models.ApplicationSession, pk=kwargs['session_id'])
        questions = app_session.questions()
        simple_fields = [
            'first_name', 'last_name', 'preferred_name',
            'email', 'phone_number'
        ]
        data = dict()
        data['answers'] = OrderedDict()
        mistakes = []
        data['is_past_applicant'] = (request.POST.get('is_past_applicant', '') == 'on')
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
                    if fn != 'verified_past_applicant' and fn != 'answers':
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

    def get_context_data(self, **kwargs):
        app_session: models.ApplicationSession = get_object_or_404(models.ApplicationSession, pk=kwargs['session_id'])
        ctx = {
            'session': app_session
        }
        return ctx
