from django.core.signing import Signer, BadSignature
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import render, redirect

from users.decorators import current_member_required

import finance.qbo as qbo


@login_required
@current_member_required
def financial_qbo_login(request: HttpRequest):
    context = {
        'qbo_login_link': qbo.qbo_auth_url(Signer().sign('qbo_login'))
    }
    return render(request, 'finance/qbo_login.html', context)


@login_required
@current_member_required
def financial_overview(request: HttpRequest):
    try:
        qbo.qbo_ensure_access_token()
    except qbo.QboNoAccess:
        return financial_qbo_login(request)
    context = qbo.get_qbo_context()
    return render(request, 'finance/overview.html', context)


@login_required
@current_member_required
def qbo_callback_view(request: HttpRequest):
    try:
        signed_state = request.GET['state'] or ''
        unsigned_state = Signer().unsign(signed_state)
        if unsigned_state != 'qbo_login':
            raise BadSignature()
    except BadSignature:
        return HttpResponseBadRequest('Invalid callback signature')
    try:
        qbo.qbo_callback(request)
    except qbo.QboNoAccess:
        return HttpResponseBadRequest('Failed to authenticate with QBO')
    return redirect('fin-overview')
