import traceback
from collections import OrderedDict
from typing import Union

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from utils.utils import is_university_email

from . import models
import re
import sys
from datetime import datetime, timedelta

import requests

from ics import Calendar, Event
import pytz

data_re = re.compile('[ a-zA-Z0-9_@.+-]*')


# def active_member_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
#     """
#     Decorator for views that checks that the user is logged in, redirecting
#     to the log-in page if necessary.
#     """
#     actual_decorator = user_passes_test(
#         lambda u: u.is_authenticated and u.profile.current_member,
#         login_url=login_url,
#         redirect_field_name=redirect_field_name
#     )
#     if function:
#         return actual_decorator(function)
#     return actual_decorator


class BasementBookingFormView(TemplateView):
    template_name = 'basement_booking_form/basement_booking_form.html'
    success_template_name = 'basement_booking_form/success.html'

    def post(self, request: HttpRequest, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)

        errors = []
        warnings = []

        responses = dict()
        # Contact Details
        responses['name'] = request.POST.get('name', '')
        responses['group_name'] = request.POST.get('group_name', '')
        responses['email'] = request.POST.get('email', '')
        responses['phone_number'] = request.POST.get('phone_number', '')
        responses['is_current_member'] = request.POST.get('is_current_member', '')

        # Event Details
        responses['event_name'] = request.POST.get('event_name', '')   
        responses['event_description'] = request.POST.get('event_description', '')
        responses['booking_start_time'] = request.POST.get('booking_start_time', '')
        responses['booking_end_time'] = request.POST.get('booking_end_time', '')
        responses['is_event_public'] = request.POST.get('is_event_public', '')
        responses['is_event_ticketed'] = request.POST.get('is_event_ticketed', '')

        # Support Requirements
        responses['equipment'] = request.POST.get('equipment', '')
        responses['sound_system_induction'] = request.POST.get('sound_system_induction', '')

        # Disclaimers and Finances
        responses['licencing'] = request.POST.get('licencing', '')
        responses['deposit_agreement'] = request.POST.get('deposit_agreement', '')
        responses['safer_spaces_agreement'] = request.POST.get('safer_spaces_agreement', '')

        try:
            tentative_calendar_url = "https://nextcloud.eshc.coop/remote.php/dav/public-calendars/a4DioSMHXiqfo7iZ?export"
            tentative_calendar_ics = requests.get(tentative_calendar_url).text
            tentative_calendar = Calendar(tentative_calendar_ics)
        except Exception as e:
            print(f"Error fetching tentative calendar: {e}")
            errors.append("Failed to fetch tentative calendar data.")

        try:
            # TODO GET CORRECT LINK
            firm_calendar_url = "https://nextcloud.eshc.coop/remote.php/dav/public-calendars/a4DioSMqfo7iZ?export"
            firm_calendar_ics = requests.get(firm_calendar_url).text
            firm_calendar = Calendar(firm_calendar_ics)
        except Exception as e:
            print(f"Error fetching tentative calendar: {e}")
            errors.append("Failed to fetch tentative calendar data.")
            ctx['error_message'] = 'An error occurred, please try again later: ' + ', '.join(
                errors)
            return self.render_to_response(ctx)
        

        print('responses', responses)

        # Validate responses
        try:
            # Parse booking start and end times

            # Side-note for PR, I HATE datetime parsing in Python.
            # Will this code work when the clocks change?
            # This I leave as exercise to the reviewer.

            bst = pytz.timezone('Europe/London')
            booking_start = datetime.strptime(responses['booking_start_time'], '%Y-%m-%dT%H:%M').replace(tzinfo=bst)
            booking_end = datetime.strptime(responses['booking_end_time'], '%Y-%m-%dT%H:%M').replace(tzinfo=bst)

            # Check if the booking start time is after today
            print(datetime.now(tz=bst))
            if booking_start < datetime.now(tz=pytz.UTC):
                errors.append("The booking start time must be in the future.")
            
            # Check if the booking start time is within a year from now
            if booking_start > datetime.now(tz=pytz.UTC) + timedelta(days=365):
                errors.append("The booking start time must be within a year from today.")

            # Check if the booking duration is at most 24 hours
            if booking_end - booking_start > timedelta(hours=24):
                errors.append("The booking duration cannot exceed 24 hours.")
            elif booking_end <= booking_start:
                errors.append("The booking end time must be after the start time.")

            # check if there are any existing tentative bookings that overlap with this one
            for event in tentative_calendar.events:
                # Check if the event overlaps with the booking time
                if (event.begin < booking_end and event.end > booking_start) or \
                   (event.begin == booking_start or event.end == booking_end):
                    if event.name == responses['event_name']:
                        errors.append("An event with this name at this time already exists in the calendar.")
                    else:
                        warnings.append(f"Tentative event '{event.name}' overlaps with your booking time: {event.begin} - {event.end}.")
                
            # check if there are any existing firm bookings that overlap with this one
            for event in firm_calendar.events:
                # Check if the event overlaps with the booking time
                if (event.begin < booking_end and event.end > booking_start) or \
                   (event.begin == booking_start or event.end == booking_end):
                    if event.name == responses['event_name']:
                        errors.append("An event with this name at this time already exists in the calendar.")
                    else:
                        warnings.append(f"Tentative event '{event.name}' overlaps with your booking time: {event.begin} - {event.end}.")
                
        except ValueError as e:
            errors.append("Invalid date format for booking times. Please use 'YYYY-MM-DD HH:MM:SS'.")

        print('errors', errors)
        print('warnings', warnings)
        # TODO compose email confirmation
        # TODO compose email to basement booking team

        # TODO Add event to event list
        # TODO Add event to calendar
        

        # data = dict()
        # mistakes = []
        # data['answers'] = OrderedDict()
        # for q in questions:
        #     qname = 'question_%d' % (q.pk,)
        #     if q.question_type == models.QuestionType.MultipleChoice.name:
        #         data['answers'][q.pk] = request.POST.getlist(qname, [])
        #     else:
        #         data['answers'][q.pk] = request.POST.getlist(qname, [''])[0]

        #     # create corresponding response entry
        #     if q.question_type == models.QuestionType.LongText.name or q.question_type == models.QuestionType.ShortText.name:
        #         r = models.CensusResponse.objects.create(session=app_session, question=q, answer_text=data['answers'][q.pk])
        #     elif q.question_type == models.QuestionType.SingleChoice.name:
        #         # find corresponding int key in option array
        #         options = q.options_array()
        #         try:
        #             i = options.index(data['answers'][q.pk])
        #             r = models.CensusResponse.objects.create(session=app_session, question=q, answer_choice=i)
        #         except ValueError:
        #             mistakes.append(q.question_text)
        #     elif q.question_type == models.QuestionType.MultipleChoice.name:
        #         options = q.options_array()
        #         for a in data['answers'][q.pk]:
        #                 # find corresponding int key in option array
        #                 try:
        #                     i = options.index(a)
        #                     r = models.CensusResponse.objects.create(session=app_session, question=q, answer_choice=i)
        #                 except ValueError:
        #                     mistakes.append(q.question_text)
        #     r.refresh_from_db()

        # for k, v in data.items():
        #     ctx[k] = v
        # ctx['num_mistakes'] = len(mistakes)
        # if len(mistakes) > 0:
        #     ctx['error_message'] = 'Please correct some of your answers below. Mistakes in fields: ' + ', '.join(
        #         mistakes)
        #     return self.render_to_response(ctx)
        # else:
        #     r = models.CensusSession.objects.get(pk=app_session.id)
        #     r.response_count += 1
        #     r.save()
        #     response = render(request, self.success_template_name, ctx, self.content_type)
        #     response.set_cookie(key='census_%s_filled' % (app_session.id), value=True)
        #     return response

    def get_context_data(self, **kwargs) -> dict:
        app_session: models.BasementBookingFormSession = get_object_or_404(models.BasementBookingFormSession)
        ctx = {
            'session': app_session
        }
        return ctx