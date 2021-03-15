from django.urls import reverse

from ..views import apis


def view_pending_account(client):
    req = client.post(
            reverse(apis.get_pending_bank_accounts),
            content_type='application/json',
            data={})
    return req


def approve_account(client, req_data, number):
    req = client.post(
        reverse(apis.approve_bank_account),
        data={'account_number': req_data[number]['account'],
              'approved': True,
              'back': 'foo'})
    return req
