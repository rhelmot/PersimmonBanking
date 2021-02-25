from django.test import TestCase, Client
from django.urls import reverse

from ..models import EmployeeLevel
from .. import views
from ..common import make_user


class TestUserInformation(TestCase):
    def test_user_information(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        make_user('user')
        admin = Client()
        self.assertTrue(admin.login(username='admin', password='password'))
        client = Client()
        self.assertTrue(client.login(username='user', password='password'))

        # test if client can change there address successfully
        req = client.post(
            reverse(views.change_my_address),
            content_type='application/json',
            data={'new_address': '123 fake street'})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        # print(req_data)
        self.assertEqual(req_data, {'my new address': '123 fake street'})

        # test if client can change there phone number
        req = client.post(
            reverse(views.change_my_phone),
            content_type='application/json',
            data={'new_phone': '0987654321'})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        # print(req_data)
        self.assertEqual(req_data, {'my new phone': '0987654321'})

        # test if client can change there email
        req = client.post(
            reverse(views.change_my_email),
            content_type='application/json',
            data={'new_email': 'new@example.com'})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        # print(req_data)
        self.assertEqual(req_data, {'my new email': 'new@example.com'})
