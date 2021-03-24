from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
import sms

from ..views import apis
from ..models import EmployeeLevel, UserEditRequest, User
from ..common import make_user


class TestUserInformation(TestCase):
    def test_user_information(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        user = make_user('user')
        admin = Client()
        self.assertTrue(admin.login(username='admin', password='password'))
        client = Client()
        self.assertTrue(client.login(username='user', password='password'))

        # test if client can change their address successfully
        req = client.post(
            reverse(apis.edit_user, args=(user.id,)),
            data={'address': '123 fake street'})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(UserEditRequest.objects.all()), 1)

        # test if client can change their phone number
        req = client.post(
            reverse(apis.edit_user, args=(user.id,)),
            data={'phone': '0987654321'})
        self.assertEqual(req.status_code, 200)
        code1 = sms.outbox[-2].body.split()[-1]  # pylint: disable=no-member
        code2 = sms.outbox[-1].body.split()[-1]  # pylint: disable=no-member
        req = client.post(
            reverse(apis.edit_user, args=(user.id,)),
            data={'phone': '0987654321',
                  'phone_verification_1': code1,
                  'phone_verification_2': code2})
        self.assertEqual(User.objects.get(id=user.id).phone, '0987654321')

        # test if client can change their email
        req = client.post(
            reverse(apis.edit_user, args=(user.id,)),
            data={'email': 'new@example.com'})
        self.assertEqual(req.status_code, 200)
        code1 = mail.outbox[0].body.split()[-1]
        code2 = mail.outbox[1].body.split()[-1]
        req = client.post(
            reverse(apis.edit_user, args=(user.id,)),
            data={'email': 'new@example.com',
                  'email_verification_1': code1,
                  'email_verification_2': code2})
        self.assertEqual(User.objects.get(id=user.id).email, 'new@example.com')
