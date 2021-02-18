from django.test import TestCase, Client
from django.urls import reverse

from ..models import User, EmployeeLevel, DjangoUser, AccountType, ApprovalStatus
from .. import views

def make_user(username,
              first_name='Firstname',
              last_name='Lastname',
              password='password',
              email='example@example.com',
              phone='0000000000',
              address='nowhere',
              employee_level=EmployeeLevel.CUSTOMER) -> User:
    """
    A function for quickly creating a user with a bunch of testing defaults set.
    """
    django_user = DjangoUser.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password)
    return User.objects.create(
        phone=phone,
        address=address,
        employee_level=employee_level,
        django_user=django_user)


class TestUserInformation(TestCase):
    def test_UserInformation(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        make_user('user')
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))

        # test if client can change there address successfully
        req = client_user.post(
            reverse(views.change_my_address),
            content_type='application/json',
            data={'new_address': '123 fake street'})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        print(req_data)
        self.assertEqual(req_data, {'my new address': '123 fake street'})

        # test if client can change there phone number
        req = client_user.post(
            reverse(views.change_my_phone),
            content_type='application/json',
            data={'new_phone': '0987654321'})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        print(req_data)
        self.assertEqual(req_data, {'my new phone': '0987654321'})

        # test if client can change there email
        req = client_user.post(
            reverse(views.change_my_email),
            content_type='application/json',
            data={'new_email': 'new@example.com'})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        print(req_data)
        self.assertEqual(req_data, {'my new email': 'new@example.com'})


        # setup and approve bank account
        req = client_user.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CHECKING})
        self.assertEqual(req.status_code, 200)
        print(req.json())
        req = client_user.post(
            reverse(views.get_my_accounts),
            content_type='application/json',
            data={})
        req_data = req.json()
        print(req_data)
        req = client_admin.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': req_data[0]['account'],
                  'approved': True})
        self.assertEqual(req.status_code, 200)
        print(req.json())
        req = client_user.post(
            reverse(views.get_my_accounts),
            content_type='application/json',
            data={})
        req_data = req.json()