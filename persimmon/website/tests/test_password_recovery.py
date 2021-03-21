import re
from django.urls import reverse
from django.test import TestCase, Client
from django.core import mail
from django.contrib.auth import views
from django.contrib.auth import authenticate

from ..common import make_user

VALID_USER_NAME = "example@example.com"


class TestPasswordRecovery(TestCase):

    def test_password_reset_ok(self):
        # ask for password reset
        make_user('user')
        client = Client()
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['pages/reset_password.html'])

        response = self.client.post(reverse('password_reset'),
                                    {"email": VALID_USER_NAME})

        # extract reset token from email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password reset on testserver')
        token = response.context[0]['token']
        uid = response.context[0]['uid']
        response = self.client.get(reverse('password_reset_confirm', kwargs={'token': token, 'uidb64': uid}))
        print(response)
        self.assertEqual(response.status_code, 302)
        #self.assertEqual(response.template_name, 'pages/reset_password_confirm.html')

        response = self.client.post(reverse('password_reset_confirm',
                                            kwargs={'token': token, 'uidb64': uid}),
                                    {'new_password1': 'pass', 'new_password2': 'pass'})

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(authenticate(username="username", password="pass"))
