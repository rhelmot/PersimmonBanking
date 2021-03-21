import re

from django.urls import reverse, NoReverseMatch
from django.test import TestCase, Client
from django.core import mail
from django.test.utils import override_settings
from django.contrib.auth import authenticate

from ..common import make_user

VALID_USER_NAME = "username"
USER_OLD_PSW = "oldpassword"
USER_NEW_PSW = "newpassword"
PASSWORD_RESET_URL = reverse("reset_password")


def password_reset_confirm_url(uidb64, token):
    try:
        return reverse("app:password_reset_confirm", args=(uidb64, token))
    except NoReverseMatch:
        return f"/accounts/reset/invaliduidb64/invalid-token/"


def utils_extract_reset_tokens(full_url):
    return re.findall(r"/([\w\-]+)",
                      re.search(r"^http\://.+$", full_url, flags=re.MULTILINE)[0])[3:5]


def test_password_reset_ok(self):
    make_user('username', password='password', phone="+14809557649")
    client = Client()
    # ask for password reset
    response = self.client.post(PASSWORD_RESET_URL,
                                {"email": "example@example.com"},
                                follow=True)

    # extract reset token from email
    self.assertEqual(len(mail.outbox), 1)
    msg = mail.outbox[0]
    uidb64, token = utils_extract_reset_tokens(msg.body)

    # change the password
    self.client.get(password_reset_confirm_url(uidb64, token), follow=True)
    response = self.client.post(password_reset_confirm_url(uidb64, "set-password"),
                                {
                                    "new_password1": USER_NEW_PSW,
                                    "new_password2": USER_NEW_PSW},
                                follow=True)

    self.assertIsNone(authenticate(username=VALID_USER_NAME,password=USER_NEW_PSW))


