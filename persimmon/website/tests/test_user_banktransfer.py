from django.test import TestCase, Client
from django.urls import reverse

from ..views import html_views
from ..models import EmployeeLevel, BankAccount, AccountType, Transaction, ApprovalStatus
from ..common import make_user, do_approval


class TestUserBankTransfer(TestCase):
    def test_user_bank_transfer(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        user1 = make_user('user1')
        client_user1 = Client()
        self.assertTrue(client_user1.login(username='user1', password='password'))
        user2 = make_user('user2')
        client_user2 = Client()
        self.assertTrue(client_user2.login(username='user2', password='password'))

        BankAccount.objects.create(
            owner=user1,
            type=AccountType.CHECKING,
            approval_status=ApprovalStatus.APPROVED,
            balance=1000)
        BankAccount.objects.create(
            owner=user2,
            type=AccountType.CHECKING,
            approval_status=ApprovalStatus.APPROVED,
            balance=500)

        # check for error if transfer to much funds
        req = client_user1.post(
            reverse(html_views.transfer_page),
            data={'account_1': 1, 'amount': 1001, 'account_2': 2, 'transfer_type': 'SEND'})
        do_approval(client_user1, Transaction.objects.last().id)
        self.assertEqual(Transaction.objects.last().transaction, 1001)
        self.assertEqual(Transaction.objects.last().approval_status, ApprovalStatus.PENDING)

        # check that balance has not changed
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        current_balance = account1.balance
        self.assertEqual(current_balance, 1000)
        account2 = allofthem[1]
        current_balance = account2.balance
        self.assertEqual(current_balance, 500)

        # check error for accounts do not belong to client 1
        count = len(Transaction.objects.all())
        req = client_user1.post(
            reverse(html_views.transfer_page),
            data={'account_1': 2, 'amount': 10, 'account_2': 1, 'transfer_type': 'SEND'})
        self.assertEqual(len(Transaction.objects.all()), count)
        account1, account2 = BankAccount.objects.all()
        self.assertEqual(account1.balance, 1000)
        self.assertEqual(account2.balance, 500)

        # check error for account1 does not exist
        req = client_user1.post(
            reverse(html_views.transfer_page),
            data={'account_1': 3, 'amount': 10, 'account_2': 1, 'transfer_type': 'SEND'})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(Transaction.objects.all()), count)
        account1, account2 = BankAccount.objects.all()
        self.assertEqual(account1.balance, 1000)
        self.assertEqual(account2.balance, 500)

        # check error for account 2 does not exist
        req = client_user1.post(
            reverse(html_views.transfer_page),
            data={'account_1': 1, 'amount': 10, 'account_2': 4, 'transfer_type': 'SEND'})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(len(Transaction.objects.all()), count)
        account1, account2 = BankAccount.objects.all()
        self.assertEqual(account1.balance, 1000)
        self.assertEqual(account2.balance, 500)

        # check for if no error
        req = client_user1.post(
            reverse(html_views.transfer_page),
            data={'account_1': 1, 'amount': 10, 'account_2': 2, 'transfer_type': 'SEND'})
        self.assertEqual(len(Transaction.objects.all()), count + 1)
        do_approval(client_user1, Transaction.objects.last().id)
        account1, account2 = BankAccount.objects.all()
        self.assertEqual(account1.balance, 990)
        self.assertEqual(account2.balance, 510)

        # check if transactions were created
        all_statements = Transaction.objects.filter(approval_status=ApprovalStatus.APPROVED).all()
        self.assertEqual(len(all_statements), 1)

        self.assertEqual(all_statements[0].description, 'transfer from 0000000000000001 to 0000000000000002')
        self.assertEqual(all_statements[0].approval_status, ApprovalStatus.APPROVED)
        self.assertEqual(all_statements[0].balance_subtract, 990.00)
        self.assertEqual(all_statements[0].account_subtract, account1)
        self.assertEqual(all_statements[0].balance_add, 510.00)
        self.assertEqual(all_statements[0].account_add, account2)
