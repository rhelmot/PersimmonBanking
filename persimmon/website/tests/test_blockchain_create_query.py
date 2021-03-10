from .. import views

from django.test import TestCase, Client
from django.urls import reverse
from ..common import make_user
from ..models import EmployeeLevel


class TestAccountWorkflow(TestCase):
    """
    Test the workflow for creating a bank account and accessing statements
    """

    def test_workflow(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        make_user('user')
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))

        # create bank statement to the blockchain network test case, success
        req = client_user.post(
            reverse(views.create_bank_statement_to_blockchain),
            content_type='application/json',
            data={"transaction_id": 13245644235, "date": "2021", "transaction": 100, "balance": 200
                , "account_id": 123456, "description": "credit"})
        self.assertEqual(req.status_code, 200)

        # create bank statement to the blockchain network test case fail due to missing parameters.
        # req2 = client_user.post(
        #     reverse(views.create_bank_statement_to_blockchain),
        #     content_type='application/json',
        #     data={"transaction_id": 13245644235, "date": "2021", "transaction": 100, "balance": 200
        #         , "account_id": 123456})
        # self.assertEqual(req2.status_code, 400)

        # get bank statement from blockchain successfully
        req = client_user.post(
            reverse(views.get_bank_statement_from_blockchain),
            content_type='application/json',
            data={"account_id": 123456789})
        self.assertEqual(req.status_code,200)

        # get bank statement from blockchain failed due to missing parameter.
        # req = client_user.post(
        #     reverse(views.get_bank_statement_from_blockchain),
        #     content_type='application/json',
        #     data={})
        # self.assertEqual(req.status_code,400)