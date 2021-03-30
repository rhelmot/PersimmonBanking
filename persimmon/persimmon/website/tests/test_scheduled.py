from django.test import TestCase, Client
from django.urls import reverse

from ..views import html_views
from ..models import EmployeeLevel, Appointment
from ..common import make_user


class TestSchedule(TestCase):
    def test_schedule(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        make_user('teller', employee_level=EmployeeLevel.TELLER)
        client_teller = Client()
        self.assertTrue(client_teller.login(username='teller', password='password'))
        make_user('teller1', employee_level=EmployeeLevel.TELLER)
        client_teller1 = Client()
        self.assertTrue(client_teller1.login(username='teller1', password='password'))
        make_user('user')
        client_user1 = Client()
        self.assertTrue(client_user1.login(username='user', password='password'))
        make_user('user1')
        client_user2 = Client()
        self.assertTrue(client_user2.login(username='user1', password='password'))

        # creating appointments
        req = client_user1.post(
            reverse(html_views.schedule_appointment_page),
            data={"time": "2021-03-15 14:30"})
        self.assertEqual(req.status_code, 200)

        req = client_user2.post(
            reverse(html_views.schedule_appointment_page),
            data={"time": "2021-03-15 14:30"})
        self.assertEqual(req.status_code, 200)

        self.assertEqual(Appointment.objects.count(), 2)

    def test_schedule1(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        make_user('teller', employee_level=EmployeeLevel.TELLER)
        client_teller = Client()
        self.assertTrue(client_teller.login(username='teller', password='password'))
        make_user('user')
        client_user1 = Client()
        self.assertTrue(client_user1.login(username='user', password='password'))
        make_user('user1')
        client_user2 = Client()
        self.assertTrue(client_user2.login(username='user1', password='password'))

        # creating appointments
        req = client_user1.post(
            reverse(html_views.schedule_appointment_page),
            data={"time": "2021-03-15 14:30"})
        self.assertEqual(req.status_code, 200)

        req = client_user2.post(
            reverse(html_views.schedule_appointment_page),
            data={"time": "2021-03-16 14:30"})
        self.assertEqual(req.status_code, 200)

        self.assertEqual(Appointment.objects.count(), 2)

    def test_schedule2(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        make_user('teller', employee_level=EmployeeLevel.TELLER)
        client_teller = Client()
        self.assertTrue(client_teller.login(username='teller', password='password'))
        make_user('user')
        client_user1 = Client()
        self.assertTrue(client_user1.login(username='user', password='password'))
        make_user('user1')
        client_user2 = Client()
        self.assertTrue(client_user2.login(username='user1', password='password'))

        # creating appointments
        req = client_user1.post(
            reverse(html_views.schedule_appointment_page),
            data={"time": "2021-03-15 14:30"})
        self.assertEqual(req.status_code, 200)

        req = client_user2.post(
            reverse(html_views.schedule_appointment_page),
            data={"time": "2021-03-15 14:30"})
        self.assertEqual(req.status_code, 200)

        self.assertEqual(Appointment.objects.count(), 1)
