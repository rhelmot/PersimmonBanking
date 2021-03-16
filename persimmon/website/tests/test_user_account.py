from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail

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
            "password": "passwordA1!",
            "confirm_password": "passwordA1!",
            "email": "test@example.com",
            "phone": "4803333141",
            "address": "address"})
        self.assertEqual(len(User.objects.all()), 1)  # assert that account has been created
        self.assertEqual(len(mail.outbox), 1)  # assert that a verification email was sent

        # test that we can't create a user account due to missing parameters
        req = client.post(reverse(html_views.create_user_page), data={
            "username": "gdeshpande",
            "first_name": "Gaurav",
            "last_name": "Deshpande",
            "password": "passwordA1!",
            "confirm_password": "passwordA1!",
            "phone": "4803333141",
            "address": "address"})
        self.assertEqual(len(User.objects.all()), 1)  # assert that account has NOT been created

        # test that we can't create a user account due to failed validation
        req = client.post(reverse(html_views.create_user_page), data={
            "username": "gdeshpande",
            "first_name": "Gaurav",
            "last_name": "Deshpande",
            "password": "password111",  # not a valid password
            "confirm_password": "password111",
            "email": "test@example.com",
            "phone": "4803333141",
            "address": "address"})
        self.assertEqual(len(User.objects.all()), 1)  # assert that account has NOT been created

        # test account verification
        self.assertFalse(User.objects.get().email_verified)
        verify_url = mail.outbox[0].body.split()[-1]
        req = client.get(verify_url)
        self.assertEqual(req.status_code, 200)
        self.assertTrue(User.objects.get().email_verified)
