import asyncio

from django.urls import reverse
from django.core import mail

from . import models


def make_user(username,
              first_name='Firstname',
              last_name='Lastname',
              password='password',
              email='example@example.com',
              phone='0000000000',
              address='nowhere',
              employee_level=0) -> 'models.User':
    """
    A function for quickly creating a user with a bunch of testing defaults set.
    """
    django_user = models.DjangoUser.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password)
    return models.User.objects.create(
        phone=phone,
        address=address,
        employee_level=employee_level,
        django_user=django_user)


def do_approval(client, tid):
    client.post(reverse('approve-transaction-page', args=(tid,)), {
        'approved': True,
    })
    code = mail.outbox[-1].body.split()[-1]  # pylint: disable=no-member
    client.post(reverse('approve-transaction-page', args=(tid,)), {
        'approved': True,
        'email_verification': code,
    })


def event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop
