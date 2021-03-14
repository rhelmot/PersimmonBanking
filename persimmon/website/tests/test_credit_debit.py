from django.test import TestCase, Client
from django.urls import reverse

import persimmon.website.views.apis
from .test_bank_account import make_user
from ..models import EmployeeLevel, AccountType, BankAccount, ApprovalStatus


class TestCreditDebitWorkFlow(TestCase):
    """
    Test the workflow for making a credit and debit
    """

    def test_workflow(self):
        user = make_user('user')
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))

        account = BankAccount.objects.create(type=AccountType.CREDIT, owner=user, approval_status=ApprovalStatus.APPROVED)

        # test that can't make credit request due to missing parameters
        req = client_user.post(reverse(persimmon.website.views.apis.credit_debit_funds), content_type="application/json",
                               data={"account_id": account.id})
        self.assertEqual(req.status_code, 400)

        # test that successfully making credit request
        req = client_user.post(reverse(persimmon.website.views.apis.credit_debit_funds), content_type="application/json",
                               data={"account_id": account.id, "transactionvalue": -100.0})
        self.assertEqual(req.status_code, 200)
        assert 'error' not in req.json()

        # test that successfully making debit request
        req = client_user.post(reverse(persimmon.website.views.apis.credit_debit_funds), content_type="application/json",
                               data={"account_id": account.id, "transactionvalue": 100.0})
        self.assertEqual(req.status_code, 200)
        assert 'error' not in req.json()

        # test that can get pending transaction
        req = client_admin.post(reverse(persimmon.website.views.apis.get_pending_transactions), content_type="application/json",
                                data={"account_id": account.id})
        self.assertEqual(req.status_code, 200)
        req_pending_data = req.json()

        # test that can approve pending transaction
        req = client_admin.post(reverse(persimmon.website.views.apis.approve_transaction), content_type="application/json",
                                data={"transaction_id": req_pending_data[0]["transactionid"],
                                      "approved": True})
        self.assertEqual(req.status_code, 200)
        self.assertNotIn("error", req.json())
