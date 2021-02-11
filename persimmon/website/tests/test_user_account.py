from django.test import TestCase, Client
from django.urls import reverse

from ..models import EmployeeLevel, User
from .. import views


#
# def make_user(username,
#               first_name='Firstname',
#               last_name='Lastname',
#               password='password',
#               email='example@example.com',
#               phone='0000000000',
#               address='nowhere',
#               employee_level=EmployeeLevel.CUSTOMER) -> User:
#     """
#         A function for quickly creating a user with a bunch of testing defaults set.
#         """
#     django_user = DjangoUser.objects.create_user(
#         username=username,
#         first_name=first_name,
#         last_name=last_name,
#         email=email,
#         password=password)
#     return User.objects.create(
#         phone=phone,
#         address=address,
#         employee_level=employee_level,
#         django_user=django_user)


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


