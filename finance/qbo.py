"""
Quickbooks API wrappers
"""
from django.http import HttpRequest
from django.http.response import HttpResponseBadRequest

from .models import FinanceConfig
from django.contrib.sites.models import Site
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
from quickbooks import QuickBooks
import quickbooks.objects as qb
from eshcIntranet.settings import *
from datetime import timedelta


def qbo_redirect_uri():
    domain = Site.objects.get_current().domain
    protocol = 'https'
    if domain == 'localhost:8000':
        protocol = 'http'
    return '%s://%s/finance/qbo_callback' % (protocol, domain)


auth_client = AuthClient(
    client_id=QBO_CLIENT_ID,
    client_secret=QBO_CLIENT_SECRET,
    environment=QBO_ENVIRONMENT,
    redirect_uri=qbo_redirect_uri()
)

scopes = [Scopes.ACCOUNTING]


class QboNoAccess(Exception):
    pass


def qbo_auth_url(csrf):
    return auth_client.get_authorization_url(scopes, csrf)


def qbo_ensure_access_token():
    fc = FinanceConfig.load()
    access_token = fc.get_access_token()
    if access_token is not None and len(access_token) > 0:
        return access_token
    refresh_token = fc.get_refresh_token()
    if refresh_token is None or len(refresh_token) == 0:
        raise QboNoAccess
    try:
        auth_client.refresh(refresh_token)
        fc.qboRefreshToken = auth_client.refresh_token
        fc.qboAccessToken = auth_client.access_token
        fc.qboRefreshTimeout = timezone.now() + timedelta(days=179)
        fc.qboAccessTimeout = timezone.now() + timedelta(minutes=59)
        fc.save()
    except AuthClientError:
        raise QboNoAccess


def qbo_callback(request: HttpRequest):
    realm_id = request.GET['realmId']
    code = request.GET['code']
    if realm_id is None or code is None:
        raise Exception('Invalid response')
    auth_client.get_bearer_token(code, realm_id)
    access_token = auth_client.access_token
    refresh_token = auth_client.refresh_token
    fc = FinanceConfig.load()
    FinanceConfig.objects.filter(pk=fc.pk).update(
        qboRealmId=realm_id,
        qboAccessToken=access_token,
        qboRefreshToken=refresh_token,
        qboAccessTimeout=timezone.now() + timedelta(minutes=59),
        qboRefreshTimeout=timezone.now() + timedelta(days=179)
    )


def get_qbo_context():
    fc = FinanceConfig.load()
    q = QuickBooks(
        auth_client=auth_client,
        refresh_token=fc.qboRefreshToken,
        company_id=fc.qboRealmId,
        minorversion=41,
    )
    pay_per_cust = dict()
    total_pay = 0.0
    lim_date = (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    payments = qb.Payment.query("""SELECT * FROM Payment WHERE TxnDate >= '%s'""" % (lim_date, ), qb=q)
    for p in payments:
        amt = p.TotalAmt
        cname = p.CustomerRef.name
        pay_per_cust[cname] = pay_per_cust.get(cname, 0.0) + amt
        total_pay += amt
    for k in pay_per_cust:
        pay_per_cust[k] = pay_per_cust[k] / total_pay * float(fc.monthlyRent)
    return {
        'pay_per_cust': pay_per_cust
    }
