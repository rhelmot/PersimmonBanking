from django.test import TestCase, Client
from django.urls import reverse

from common_test_functions import make_user
from .. import views

class TestSessions(TestCase):
    @staticmethod
    def is_logged_in(client):
        return client.post(
            reverse(views.login_status),
            content_type='application/json',
            data={}).json()['logged_in']

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
