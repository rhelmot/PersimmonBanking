from django.test import TestCase, Client
from django.urls import reverse

from .test_bank_account import make_user
from ..models import EmployeeLevel, AccountType
from .. import views


class TestCreditDebitWorkFlow(TestCase):
    """
    Test the workflow for making a credit and debit
    """

    def test_workfolow(self):
        make_user('user')
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        req1 = client_user.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CREDIT})
        self.assertEqual(req1.status_code, 200)
        req_data = req1.json()

        # test that can't make credit request due to missing parameters#
        req = client_user.post(reverse(views.credit_debit_funds), content_type="application/json",
                               data={"account_id": req_data["account"]})
        self.assertEqual(req.status_code, 400)

        # test that successfully making credit request#
        req = client_user.post(reverse(views.credit_debit_funds), content_type="application/json",
                               data={"account_id": req_data["account"], "transactionvalue": 500.0})
        self.assertEqual(req.status_code, 200)

        # test that successfully making debit request#
        req = client_user.post(reverse(views.credit_debit_funds), content_type="application/json",
                               data={"account_id": req_data["account"], "transactionvalue": 100.0})
        self.assertEqual(req.status_code, 200)

        # test that can get pending transaction#
        req = client_admin.post(reverse(views.get_pending_transactions), content_type="application/json",
                                data={"account_id": req_data['account']})
        self.assertEqual(req.status_code, 200)
        req_pending_data = req.json()
        print(req_pending_data)
        # test that can approve pending transaction and create bank statement to blockchain#
        # before you test this please bring the blockchain network up#
        req = client_admin.post(reverse(views.approve_credit_debit_funds), content_type="application/json",
                                data={"transaction_id": req_pending_data[0]["transactionid"],
                                      "approved": True})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(req.json()[0]), 6)

        # test that can get data from the blockchain successfully#
        # before you test this please bring the blockchain network up#
        req = client_user.post(
            reverse(views.get_bank_statement_from_blockchain),
            content_type='application/json',
            data={"account_id": req_pending_data[0]["accountId"]})
        self.assertEqual(req.status_code, 200)

