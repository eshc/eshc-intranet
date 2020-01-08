"""
Quickbooks API wrappers
"""
from django.http import HttpRequest
from django.http.response import HttpResponseBadRequest

from .models import FinanceConfig
from django.contrib.sites.models import Site
from django.core.cache import cache
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError
from quickbooks import QuickBooks
import quickbooks.objects as qb
from eshcIntranet.settings import *
import datetime
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
        auth_client.access_token = access_token
        auth_client.refresh_token = fc.get_refresh_token()
        return access_token
    refresh_token = fc.get_refresh_token()
    if refresh_token is None or len(refresh_token) == 0:
        raise QboNoAccess
    try:
        auth_client.refresh(refresh_token)
        fc.qboRefreshToken = auth_client.refresh_token
        fc.qboAccessToken = auth_client.access_token
        fc.qboRefreshTimeout = timezone.now() + timedelta(days=100)
        fc.qboAccessTimeout = timezone.now() + timedelta(minutes=59)
        fc.save()
    except AuthClientError:
        raise QboNoAccess


def qbo_callback(request: HttpRequest):
    fc = FinanceConfig.load()
    realm_id = request.GET.get('realmId', fc.qboRealmId)
    code = request.GET.get('code', None)
    if realm_id is None or code is None:
        raise QboNoAccess('Invalid response')
    auth_client.get_bearer_token(code, realm_id)
    access_token = auth_client.access_token
    refresh_token = auth_client.refresh_token
    FinanceConfig.objects.filter(pk=fc.pk).update(
        qboRealmId=realm_id,
        qboAccessToken=access_token,
        qboRefreshToken=refresh_token,
        qboAccessTimeout=timezone.now() + timedelta(minutes=59),
        qboRefreshTimeout=timezone.now() + timedelta(days=179)
    )


MACRO_THIS_YEAR = 'This Fiscal Year'
MACRO_LAST_YEAR = 'Last Fiscal Year'


def try_float(d):
    if len(str(d).strip()) == 0:
        return 0.0
    try:
        return float(d)
    except ValueError:
        print("Invalid float: ", str(d))
        return 0.0


def qbo_profit_loss_report(q: QuickBooks, fc: FinanceConfig, macro: str):
    pal = q.get_report('ProfitAndLoss', qs={'summarize_column_by': 'Classes', 'date_macro': macro})
    agg = {
        # 'raw': pal,
        'classes': [c['ColTitle'] for c in pal['Columns']['Column'][1:-1]],
        'start_date': datetime.datetime.strptime(pal['Header']['StartPeriod'], "%Y-%m-%d"),
        'end_date': datetime.datetime.strptime(pal['Header']['EndPeriod'], "%Y-%m-%d"),
        'total_income': 0.0,
        'total_expenses': 0.0,
        'rent_avg_value': 0.0,
        'rent_eqv_divider': 1.0,
        'unused_income': 0.0,
        'expense_labels': list(),
        'expense_data': list(),
        'expense_totals': list(),
        'class_totals': list(),
    }
    # Total income
    for row in pal['Rows']['Row']:
        if row.get('group', '') == 'Income':
            agg['total_income'] = try_float(row['Summary']['ColData'][-1]['value'])
            break
    # Process expense rows
    erow = False
    for toprow in pal['Rows']['Row']:
        if toprow.get('group', '') == 'Expenses':
            erow = toprow
            break
    agg['total_expenses'] = try_float(toprow['Summary']['ColData'][-1]['value'])

    def process_row(row):
        for subrow in row['Rows']['Row']:
            if subrow.get('type', '') == 'Section':
                process_row(subrow)
            elif subrow.get('type', '') == 'Data':
                cdata = subrow['ColData']
                agg['expense_labels'].append(str(cdata[0]['value']))
                agg['expense_totals'].append(try_float(cdata[-1]['value']))
                ldata = list()
                for datum in cdata[1:-1]:
                    ldata.append(try_float(datum['value']))
                agg['expense_data'].append(ldata)

    process_row(erow)

    for i in range(len(agg['classes'])):
        agg['class_totals'].append(sum([dtr[i] for dtr in agg['expense_data']]))

    agg_days = (agg['end_date'] - agg['start_date']).days
    agg['rent_avg_value'] = agg['total_income'] * 30.5 / (fc.memberCount * agg_days)
    agg['rent_eqv_divider'] = agg['rent_avg_value'] / agg['total_expenses']
    agg['unused_income'] = agg['total_income'] - agg['total_expenses']

    return agg


def qbo_cached_profit_loss_report(q: QuickBooks, fc: FinanceConfig, macro: str):
    key = 'qbo_profit_loss_%s' % (macro.replace(' ', '_'),)
    found = cache.get(key)
    if found is not None:
        print('hit')
        return found
    print('miss')
    queried = qbo_profit_loss_report(q, fc, macro)
    cache.set(key, queried, 60*60*4)
    return queried


def qbo_clean_cache():
    cache.delete_many(['qbo_profit_loss_%s' % (macro.replace(' ', '_'),) for macro in [MACRO_THIS_YEAR, MACRO_LAST_YEAR]])


def wg_summary(report):
    agg = dict()
    for cls, data in zip(report['classes'], report['class_totals']):
        agg[cls] = {'bare': data, 'rent': data * report['rent_eqv_divider']}
    if report['unused_income'] > 0:
        agg['Unallocated income'] = {'bare': report['unused_income'],
                                     'rent': report['unused_income'] * report['rent_eqv_divider']}
    return agg


def type_summary(report):
    agg = dict()
    for cls, data in zip(report['expense_labels'], report['expense_totals']):
        agg[cls] = {'bare': data, 'rent': data * report['rent_eqv_divider']}
    if report['unused_income'] > 0:
        agg['Unallocated income'] = {'bare': report['unused_income'],
                                     'rent': report['unused_income'] * report['rent_eqv_divider']}
    return agg


def get_qbo_context():
    fc = FinanceConfig.load()
    qbo_ensure_access_token()
    q = QuickBooks(
        auth_client=auth_client,
        refresh_token=fc.qboRefreshToken,
        company_id=fc.qboRealmId,
        minorversion=41,
    )
    this_report = qbo_cached_profit_loss_report(q, fc, MACRO_THIS_YEAR)
    # last_report = qbo_cached_profit_loss_report(q, fc, MACRO_LAST_YEAR)

    return {
        'this_report': this_report,
        # 'last_report': last_report,
        'this_wg': wg_summary(this_report),
        'this_type': type_summary(this_report),
        # 'last_wg': wg_summary(last_report)
    }
