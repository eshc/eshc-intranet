from collections import OrderedDict

from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from . import models
import re
import sys

data_re = re.compile('[ a-zA-Z0-9_@.+-]*')

class CensusResultsView(TemplateView):
    template_name = 'census/census_results.html'

    def post(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        app_session: models.CensusSession = get_object_or_404(models.CensusSession, pk=kwargs['session_id'])
        if not app_session.is_census_open():
            return self.get(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs) -> dict:
        app_session: models.CensusSession = get_object_or_404(models.CensusSession, pk=kwargs['session_id'])
        ctx = {
            'session': app_session
        }
        return ctx


class CensusView(TemplateView):
    template_name = 'census/census.html'
    success_template_name = 'census/success.html'
    already_filled_template_name = 'census/already_filled.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        app_session: models.CensusSession = get_object_or_404(models.CensusSession, pk=kwargs['session_id'])
        value = bool(request.COOKIES.get('census_%s_filled' % (app_session.id)))
        if value is True:
            # Cookie is not set
            return render(request, self.already_filled_template_name, ctx, self.content_type)
        else:
            return self.render_to_response(ctx)

    def post(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        app_session: models.CensusSession = get_object_or_404(models.CensusSession, pk=kwargs['session_id'])
        if not app_session.is_census_open():
            return self.get(request, *args, **kwargs)

        questions = app_session.questions()
        data = dict()
        mistakes = []
        data['answers'] = OrderedDict()
        for q in questions:
            qname = 'question_%d' % (q.pk,)
            if q.question_type == models.QuestionType.MultipleChoice.name:
                data['answers'][q.pk] = request.POST.getlist(qname, [])
            else:
                data['answers'][q.pk] = request.POST.getlist(qname, [''])[0]

            # create corresponding response entry
            if q.question_type == models.QuestionType.LongText.name or q.question_type == models.QuestionType.ShortText.name:
                r = models.CensusResponse.objects.create(session=app_session, question=q, answer_text=data['answers'][q.pk])
            elif q.question_type == models.QuestionType.SingleChoice.name:
                # find corresponding int key in option array
                options = q.options_array()
                try:
                    i = options.index(data['answers'][q.pk])
                    r = models.CensusResponse.objects.create(session=app_session, question=q, answer_choice=i)
                except ValueError:
                    mistakes.append(q.question_text)
            elif q.question_type == models.QuestionType.MultipleChoice.name:
                options = q.options_array()
                for a in data['answers'][q.pk]:
                        # find corresponding int key in option array
                        try:
                            i = options.index(a)
                            r = models.CensusResponse.objects.create(session=app_session, question=q, answer_choice=i)
                        except ValueError:
                            mistakes.append(q.question_text)
            r.refresh_from_db()

        for k, v in data.items():
            ctx[k] = v
        ctx['num_mistakes'] = len(mistakes)
        if len(mistakes) > 0:
            ctx['error_message'] = 'Please correct some of your answers below. Mistakes in fields: ' + ', '.join(
                mistakes)
            return self.render_to_response(ctx)
        else:
            r = models.CensusSession.objects.get(pk=app_session.id)
            r.response_count += 1
            r.save()
            response = render(request, self.success_template_name, ctx, self.content_type)
            response.set_cookie(key='census_%s_filled' % (app_session.id), value=True)
            return response

    def get_context_data(self, **kwargs) -> dict:
        app_session: models.CensusSession = get_object_or_404(models.CensusSession, pk=kwargs['session_id'])
        ctx = {
            'session': app_session
        }
        return ctx