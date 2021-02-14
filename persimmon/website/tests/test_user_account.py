from django.test import TestCase, Client
from django.urls import reverse

from ..models import EmployeeLevel, User
from .. import views


class TestAccountWorkflow(TestCase):
    """
    Test the workflow for creating a user account
    """

    def test_workflow(self):
        # test that we can create a user account

        client_user1 = Client()

        req1 = client_user1.post(reverse(views.create_user_account), content_type='application/json',
                                 data={"username": "gdeshpande", "first_name": "Gaurav", "last_name": "Deshpande",
                                       "password": "password", "email": "test_email", "phone": "4803333141",
                                       "address": "address", "employee_level": EmployeeLevel.CUSTOMER})
        self.assertEqual(req1.status_code, 200)

        # test that we can't create a user account due to missing parameters

        client_user2 = Client()

        req2 = client_user2.post(reverse(views.create_user_account), content_type='application/json',
                                 data={"username": "new_user", "last_name": "Deshpande",
                                       "password": "password", "email": "test_email", "phone": "4803333141",
                                       "address": "address", "employee_level": EmployeeLevel.ADMIN})
        self.assertEqual(req2.status_code, 400)

        # test that a new user account has been created

        user_accounts = list(User.objects.all())
        self.assertEqual(len(user_accounts), 1)
