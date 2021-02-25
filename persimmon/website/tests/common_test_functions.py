from django.urls import reverse

from ..models import User, EmployeeLevel, DjangoUser, AccountType
from .. import views


def make_user(username,
              first_name='billy',
              last_name='bob',
              password='password',
              email='example@example.com',
              phone='0000000000',
              address='nowhere',
              employee_level=EmployeeLevel.CUSTOMER) -> User:

    django_user = DjangoUser.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password)

    return User.objects.create(
        phone=phone,
        address=address,
        employee_level=employee_level,
        django_user=django_user)


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


