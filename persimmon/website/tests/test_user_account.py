from django.test import TestCase, Client
from django.urls import reverse

from ..models import User, EmployeeLevel, BankAccount, DjangoUser, AccountType, ApprovalStatus


def make_user(username,
              first_name='Firstname',
              last_name='Lastname',
              password='password',
              email='example@example.com',
              phone='0000000000',
              address='nowhere',
              employee_level=EmployeeLevel.CUSTOMER) -> User:

class TestAccountWorkflow(TestCase):

    """
    Test the workflow for creating a user account
    """

    def test_workflow(self):
        # setup database
        make_user

        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        make_user('user')
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))

        # test that creating an invalid user account errors
        req = client_user.post(reverse(views.create_user_account), content_type='application/json', data= {})
