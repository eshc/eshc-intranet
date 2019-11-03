from django.core.signing import Signer
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from users.decorators import current_member_required

import finance.qbo as qbo


@login_required
@current_member_required
def financial_qbo_login(request: HttpRequest):
    context = {
        'qbo_login_link': qbo.qbo_auth_url(Signer().sign('qbo_login'))
    }
    render(request, 'finance/qbo_login.html', context)


@login_required
@current_member_required
def financial_overview(request: HttpRequest):
    qbo_access_token = ''
    try:
        qbo_access_token = qbo.qbo_get_access_token()
    except qbo.QboNoAccess:
        return financial_qbo_login(request)
    pass
