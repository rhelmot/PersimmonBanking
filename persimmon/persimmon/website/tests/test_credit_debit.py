from django.test import TestCase, Client
from django.urls import reverse

from .. import views
from ..views import apis, html_views
from .test_bank_account import make_user
from ..models import EmployeeLevel, AccountType, BankAccount, ApprovalStatus, Transaction


class TestCreditDebit(TestCase):
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
        req = client_user.post(reverse(html_views.mobile_atm_page),
                               data={"account": account.id})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(Transaction.objects.all()), 0)

        # test that successfully making credit request
        req = client_user.post(reverse(html_views.mobile_atm_page),
                               data={"account": account.id,
                                     "amount": "100",
                                     "transfer_type": "CREDIT"})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(Transaction.objects.last().transaction, 100)
        self.assertEqual(Transaction.objects.last().account_add, account)

        # test that successfully making debit request
        req = client_user.post(reverse(html_views.mobile_atm_page),
                               data={"account": account.id,
                                     "amount": "100",
                                     "transfer_type": "DEBIT"})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(Transaction.objects.last().transaction, 100)
        self.assertEqual(Transaction.objects.last().account_subtract, account)

        # test that can get pending transaction
        req = client_admin.get(reverse(html_views.employee_page))
        self.assertEqual(req.status_code, 200)
        a_transaction = Transaction.objects.filter(approval_status=ApprovalStatus.PENDING).first()
        self.assertIn('$' + str(a_transaction.transaction), req.content.decode())

        # test that can approve pending transaction
        req = client_admin.post(reverse(apis.approve_transaction),
                                data={"transaction_id": a_transaction.id,
                                      "approved": True,
                                      "back": "foo"})
        self.assertEqual(req.status_code, 200)

        # test that can get result from blockchain
        req = client_user.post(reverse(apis.get_bank_statement_from_blockchain,args=[account.id]))
        self.assertEqual(req.status_code, 200)


    def test_checks(self):
        # pylint shut upppppppppp
        # pylint: disable=invalid-name
        # set up user and account
        user = make_user('user')
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))
        acct = BankAccount.objects.create(
            owner=user,
            type=AccountType.CHECKING,
            approval_status=ApprovalStatus.APPROVED
        )

        # make four transactions. only the first should show a check
        # withdrawal with check
        t1 = Transaction.objects.create(
            transaction=10,
            account_subtract=acct,
            balance_subtract=-10,
            description='transaction 1',
            approval_status=ApprovalStatus.APPROVED,
            check_recipient='foo',
        )
        # withdrawal without check
        t2 = Transaction.objects.create(
            transaction=10,
            account_subtract=acct,
            balance_subtract=-20,
            description='transaction 2',
            approval_status=ApprovalStatus.APPROVED,
            check_recipient=None,
        )
        # deposit with check (check does nothing)
        t3 = Transaction.objects.create(
            transaction=10,
            account_add=acct,
            balance_add=-10,
            description='transaction 3',
            approval_status=ApprovalStatus.APPROVED,
            check_recipient='foo',
        )
        # pending withdrawal with check
        t4 = Transaction.objects.create(
            transaction=10,
            account_subtract=acct,
            balance_subtract=None,
            description='transaction 4',
            approval_status=ApprovalStatus.PENDING,
            check_recipient='foo',
        )

        # check that only the appropriate links show up on the statement page
        page = client_user.get(reverse(html_views.statement_page, args=(acct.id,))).content.decode()
        u1 = reverse(apis.check_image, args=(t1.id,))
        u2 = reverse(apis.check_image, args=(t2.id,))
        u3 = reverse(apis.check_image, args=(t3.id,))
        u4 = reverse(apis.check_image, args=(t4.id,))
        self.assertIn(u1, page)
        self.assertNotIn(u2, page)
        self.assertNotIn(u3, page)
        self.assertNotIn(u4, page)

        # check that only the appropriate links return an image
        c1 = client_user.get(u1).content
        c2 = client_user.get(u2).content
        c3 = client_user.get(u3).content
        c4 = client_user.get(u4).content
        self.assertEqual(c1[:4], b'\x89PNG')
        self.assertNotEqual(c2[:4], b'\x89PNG')
        self.assertNotEqual(c3[:4], b'\x89PNG')
        self.assertNotEqual(c4[:4], b'\x89PNG')
