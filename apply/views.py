from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from . import models
import re


data_re = re.compile('[ a-zA-Z0-9@.+]*')


class ApplyView(TemplateView):
    template_name = 'apply/apply.html'

    def post(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        simple_fields = [
            'first_name', 'last_name', 'preferred_name',
            'email', 'phone_number'
        ]
        print(request.POST)
        data = dict()
        num_mistakes = 0
        data['is_past_applicant'] = (request.POST.get('is_past_applicant', '') == 'on')
        for f in simple_fields:
            rqdata: str = request.POST.get(f, '')
            if re.fullmatch(data_re, rqdata) is None:
                print(f)
                data[f] = ''
                num_mistakes += 1
                continue
            data[f] = rqdata

        for k,v in data.items():
            ctx[k] = v
        ctx['num_mistakes'] = num_mistakes
        if num_mistakes > 0:
            ctx['error_message'] = 'Please correct some of your answers below.'
        return self.render_to_response(ctx)

    def get_context_data(self, **kwargs):
        app_session: models.ApplicationSession = get_object_or_404(models.ApplicationSession, pk=kwargs['session_id'])
        ctx = {
            'session': app_session
        }
        return ctx
