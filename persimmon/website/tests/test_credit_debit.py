from django.test import TestCase, Client
from django.urls import reverse

from ..views import apis, html_views
from .test_bank_account import make_user
from ..models import EmployeeLevel, AccountType, BankAccount, ApprovalStatus, Transaction


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

        account = BankAccount.objects.create(
            type=AccountType.CREDIT,
            owner=user,
            approval_status=ApprovalStatus.APPROVED)

        # test that can't make credit request due to missing parameters
        req = client_user.post(reverse(apis.credit_debit_funds), content_type="application/json",
                               data={"account_id": account.id})
        self.assertEqual(req.status_code, 400)

        # test that successfully making credit request
        req = client_user.post(reverse(apis.credit_debit_funds), content_type="application/json",
                               data={"account_id": account.id, "transactionvalue": -100.0})
        self.assertEqual(req.status_code, 200)
        assert 'error' not in req.json()

        # test that successfully making debit request
        req = client_user.post(reverse(apis.credit_debit_funds), content_type="application/json",
                               data={"account_id": account.id, "transactionvalue": 100.0})
        self.assertEqual(req.status_code, 200)
        assert 'error' not in req.json()

        # test that can get pending transaction
        req = client_admin.get(reverse(html_views.employee_page))
        self.assertEqual(req.status_code, 200)
        a_transaction = Transaction.objects.filter(approval_status=ApprovalStatus.PENDING).first()
        self.assertIn(a_transaction.description.encode(), req.content)

        # test that can approve pending transaction
        req = client_admin.post(reverse(apis.approve_transaction),
                                data={"transaction_id": a_transaction.id,
                                      "approved": True,
                                      "back": "foo"})
        self.assertEqual(req.status_code, 200)
