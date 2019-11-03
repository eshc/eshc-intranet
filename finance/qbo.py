"""
Quickbooks API wrappers
"""
from .models import FinanceConfig
from django.contrib.sites.models import Site
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
from eshcIntranet.settings import *
from datetime import timedelta

auth_client = AuthClient(
    client_id=QBO_CLIENT_ID,
    client_secret=QBO_CLIENT_SECRET,
    environment=QBO_ENVIRONMENT,
    redirect_uri='https://%s/finance/qbo_callback' % (Site.objects.get_current().domain,)
)

scopes = [Scopes.ACCOUNTING]


class QboNoAccess(Exception):
    pass


def qbo_auth_url(csrf):
    return auth_client.get_authorization_url(scopes, csrf)


def qbo_get_access_token():
    fc = FinanceConfig.load()
    accessToken = fc.get_access_token()
    if accessToken is not None and len(accessToken) > 0:
        return accessToken
    refreshToken = fc.get_refresh_token()
    if refreshToken is None or len(refreshToken) == 0:
        raise QboNoAccess
    try:
        auth_client.refresh(refreshToken)
        fc.qboRefreshToken = auth_client.refresh_token
        fc.qboAccessToken = auth_client.access_token
        fc.qboRefreshTimeout = timezone.now() + timedelta(days=179)
        fc.qboAccessTimeout = timezone.now() + timedelta(minutes=59)
        fc.save()
    except AuthClientError:
        raise QboNoAccess
    return fc.qboAccessToken


class QboAccessor:
    pass
