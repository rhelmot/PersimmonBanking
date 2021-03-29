from django.urls import reverse
from django.core import mail

from .models import User, DjangoUser, EmployeeLevel


def make_user(username,
              first_name='Firstname',
              last_name='Lastname',
              password='password',
              email='example@example.com',
              phone='0000000000',
              address='nowhere',
              employee_level=EmployeeLevel.CUSTOMER) -> User:
    """
    A function for quickly creating a user with a bunch of testing defaults set.
    """
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


def do_approval(client, tid):
    client.post(reverse('approve-transaction-page', args=(tid,)), {
        'approved': True,
    })
    code = mail.outbox[-1].body.split()[-1]
    client.post(reverse('approve-transaction-page', args=(tid,)), {
        'approved': True,
        'email_verification': code,
    })


