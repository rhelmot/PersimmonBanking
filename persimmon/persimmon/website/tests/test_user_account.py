from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
import sms

from ..views import html_views
from ..models import User


class TestAccountWorkflow(TestCase):
    """
    Test the workflow for creating a user account
    """

    def test_workflow(self):
        client = Client()

        # test that we can create a user account
        req = client.post(reverse(html_views.create_user_page), data={
            "username": "gdeshpande",
            "first_name": "Gaurav",
            "last_name": "Deshpande",
            "password1": "passwordA1!",
            "password2": "passwordA1!",
            "email": "test@example.com",
            "phone": "4803333141",
            "address": "address"})
        self.assertEqual(len(User.objects.all()), 0)  # assert that account has NOT been created
        self.assertEqual(len(mail.outbox), 1)  # assert that a verification email was sent

        # test that we can't create a user account due to missing parameters
        req = client.post(reverse(html_views.create_user_page), data={
            "username": "gdeshpande",
            "first_name": "Gaurav",
            "last_name": "Deshpande",
            "password1": "passwordA1!",
            "password2": "passwordA1!",
            # email missing
            "phone": "4803333141",
            "address": "address"})
        self.assertEqual(len(mail.outbox), 1)  # assert that a verification email was NOT sent

        # test that we can't create a user account due to failed validation
        req = client.post(reverse(html_views.create_user_page), data={
            "username": "gdeshpande",
            "first_name": "Gaurav",
            "last_name": "Deshpande",
            "password1": "password1",  # not a valid password
            "password2": "password1",
            "email": "test@example.com",
            "phone": "4803333141",
            "address": "address"})
        self.assertEqual(len(mail.outbox), 1)  # assert that a verification email was NOT sent

        # test account verification
        email_code = mail.outbox[0].body.split()[-1]
        phone_code = sms.outbox[-1].body.split()[-1]  # pylint: disable=no-member
        req = client.post(reverse(html_views.create_user_page), data={
            "username": "gdeshpande",
            "first_name": "Gaurav",
            "last_name": "Deshpande",
            "password1": "passwordA1!",
            "password2": "passwordA1!",
            "email": "test@example.com",
            "phone": "4803333141",
            "address": "address",
            "email_verification": email_code,
            "phone_verification": phone_code})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(User.objects.all()), 1)  # assert that account has been created
