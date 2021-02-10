from django.test import TestCase, Client
from django.urls import reverse

from .common import make_user
from .. import views

class TestSessions(TestCase):
    @staticmethod
    def is_logged_in(client):
        req = client.post(
            reverse(views.get_my_accounts),
            content_type='application/json',
            data={})
        if req.status_code == 200:
            return True
        if req.status_code == 404:
            return False
        raise Exception("testing error: bankaccounts/get endpoint has weird behavior")

    def test_login_logout(self):
        make_user('username', password='password')
        client = Client()

        # login with invalid creds should fail
        req = client.post(
            reverse(views.persimmon_login),
            content_type='application/json',
            data={"username": "username", "password": "wrong"})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertIn("error", req_data)
        req = client.post(
            reverse(views.persimmon_login),
            content_type='application/json',
            data={"username": "wrong", "password": "password"})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertIn("error", req_data)
        self.assertFalse(self.is_logged_in(client))

        # successful login should work
        req = client.post(
            reverse(views.persimmon_login),
            content_type='application/json',
            data={"username": "username", "password": "password"})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertNotIn("error", req_data)
        self.assertTrue(self.is_logged_in(client))

        # login should not work once you're logged in
        req = client.post(
            reverse(views.persimmon_login),
            content_type='application/json',
            data={"username": "username", "password": "password"})
        self.assertEqual(req.status_code, 404)

        # logout should work
        req = client.post(
            reverse(views.persimmon_logout),
            content_type='application/json',
            data={})
        self.assertEqual(req.status_code, 200)
        self.assertFalse(self.is_logged_in(client))

        # logout should not work once you're logged out
        req = client.post(
            reverse(views.persimmon_logout),
            content_type='application/json',
            data={})
        self.assertEqual(req.status_code, 404)
