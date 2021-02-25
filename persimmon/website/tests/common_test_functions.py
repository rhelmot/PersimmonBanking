from django.urls import reverse
from .. import views


def view_pending_account(client):
    req = client.post(
            reverse(views.get_pending_bank_accounts),
            content_type='application/json',
            data={})
    return req


def approve_account(client, req_data, number):
    req = client.post(
        reverse(views.approve_bank_account),
        content_type='application/json',
        data={'account_number': req_data[number]['account'],
              'approved': True})
    return req
