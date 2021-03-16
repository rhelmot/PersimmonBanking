from django.test import TestCase, Client
from django.urls import reverse

from ..views import apis
from ..models import EmployeeLevel, BankAccount, AccountType, Transaction, ApprovalStatus
from ..common import make_user


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
            reverse(apis.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 1, 'amount': 1001, 'accountnumb2': 2})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {"status": "pending"})

        # check that balance has not changed
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        current_balance = account1.balance
        self.assertEqual(current_balance, 1000)
        account2 = allofthem[1]
        current_balance = account2.balance
        self.assertEqual(current_balance, 500)

        # check error for accounts do not belong to client 1
        req = client_user1.post(
            reverse(apis.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 2, 'amount': 10, 'accountnumb2': 1})
        self.assertEqual(req.status_code, 200)
        self.assertIn('error', req.json())

        # check that balance has not changed
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        current_balance = account1.balance
        self.assertEqual(current_balance, 1000)
        account2 = allofthem[1]
        current_balance = account2.balance
        self.assertEqual(current_balance, 500)

        # check error for account1 does not exist
        req = client_user1.post(
            reverse(apis.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 3, 'amount': 10, 'accountnumb2': 1})
        self.assertEqual(req.status_code, 200)
        self.assertIn("error", req.json())

        # check that balance has not changed
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        current_balance = account1.balance
        self.assertEqual(current_balance, 1000)
        account2 = allofthem[1]
        current_balance = account2.balance
        self.assertEqual(current_balance, 500)

        # check error for account 2 does not exist
        req = client_user1.post(
            reverse(apis.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 1, 'amount': 10, 'accountnumb2': 4})
        self.assertEqual(req.status_code, 200)
        self.assertIn("error", req.json())

        # check that balance has not changed
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        current_balance = account1.balance
        self.assertEqual(current_balance, 1000)
        account2 = allofthem[1]
        current_balance = account2.balance
        self.assertEqual(current_balance, 500)

        # check for if no error
        req = client_user1.post(
            reverse(apis.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 1, 'amount': 10, 'accountnumb2': 2})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'status': 'complete'})
        # check that balance has not changed
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        current_balance = account1.balance
        self.assertEqual(current_balance, 990)
        account2 = allofthem[1]
        current_balance = account2.balance
        self.assertEqual(current_balance, 510)

        # check if transactions were created
        all_statements = Transaction.objects.filter(approval_status=ApprovalStatus.APPROVED).all()
        self.assertEqual(len(all_statements), 1)

        self.assertEqual(all_statements[0].description, 'transfer from 0000000000000001 to 0000000000000002')
        self.assertEqual(all_statements[0].approval_status, ApprovalStatus.APPROVED)
        self.assertEqual(all_statements[0].balance_subtract, 990.00)
        self.assertEqual(all_statements[0].account_subtract, account1)
        self.assertEqual(all_statements[0].balance_add, 510.00)
        self.assertEqual(all_statements[0].account_add, account2)
