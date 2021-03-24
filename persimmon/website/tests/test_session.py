import sms
from django.test import TestCase, Client
from django.urls import reverse
from ..views import apis, html_views
from ..common import make_user


def outbox():
    return getattr(sms, 'outbox', [])


class TestSessions(TestCase):
    @staticmethod
    def is_logged_in(client):
        return client.session.get('_auth_user_id', None) is not None

    def test_login_logout(self):
        make_user('username', password='password', phone="+14809557649")
        client = Client()
        start_sms_count = len(outbox())

        # login with invalid creds should fail
        req = client.post(
            reverse(apis.persimmon_login),
            data={"username": "username", "password": "wrong"})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(outbox()), start_sms_count)

        req = client.post(
            reverse(apis.persimmon_login),
            data={"username": "wrong", "password": "password"})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(outbox()), start_sms_count)

        # successful login should work
        req = client.post(
            reverse(apis.persimmon_login),
            data={"username": "username", "password": "password"})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(outbox()), start_sms_count + 1)

        req = client.post(
            reverse(apis.persimmon_login),
            data={"username": "username", "password": "password", "login_code": outbox()[-1].body.split()[-1]})
        self.assertEqual(req.status_code, 200)
        self.assertTrue(self.is_logged_in(client))

        # login should not work once you're logged in
        req = client.post(
            reverse(apis.persimmon_login),
            content_type='application/json',
            data={"username": "username", "password": "password"})
        self.assertEqual(req.status_code, 404)

        # logout should work
        req = client.get(reverse(html_views.logout))
        self.assertEqual(req.status_code, 200)
        self.assertFalse(self.is_logged_in(client))

        # logout should not work once you're logged out
        req = client.get(reverse(html_views.logout))
        self.assertEqual(req.status_code, 404)
