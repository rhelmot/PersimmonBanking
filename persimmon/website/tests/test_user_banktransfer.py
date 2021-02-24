from django.test import TestCase, Client
from django.urls import reverse
from ..models import User, EmployeeLevel, BankAccount, DjangoUser, AccountType, BankStatements
from .. import views
from .common_test_functions import *


class TestUserBankTransfer(TestCase):
    def test_user_bank_transfer(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        make_user('user1')
        client_user1 = Client()
        self.assertTrue(client_user1.login(username='user1', password='password'))
        make_user('user2')
        client_user2 = Client()
        self.assertTrue(client_user2.login(username='user2', password='password'))

        # add accounts for client users
        req = client_user1.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CHECKING})
        self.assertEqual(req.status_code, 200)

        req = client_user2.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CHECKING})
        self.assertEqual(req.status_code, 200)

        # approve accounts
        req = view_pending_account(client_admin)
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertIs(type(req_data), list)

        req = approve_account(client_admin, req_data, 0)
        self.assertEqual(req.status_code, 200)

        req = approve_account(client_admin, req_data, 1)
        self.assertEqual(req.status_code, 200)
        # add money to accounts
        all_acc = BankAccount.objects.all()
        account1 = all_acc[0]
        account1.balance = 1000
        account1.save()
        account2 = all_acc[1]
        account2.balance = 500
        account2.save()

        # check for error if transfer to much funds
        req = client_user1.post(
            reverse(views.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 1, 'amount': 1001, 'accountnumb2': 2})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'error': 'error insufficient funds'})
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
            reverse(views.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 2, 'amount': 10, 'accountnumb2': 1})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'error': 'account to debt does not exist or is not owned by user'})
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
            reverse(views.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 3, 'amount': 10, 'accountnumb2': 1})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'error': 'account to debt does not exist or is not owned by user'})
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
            reverse(views.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 1, 'amount': 10, 'accountnumb2': 4})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'error': 'account number 2 does not exit'})
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
            reverse(views.transfer_funds),
            content_type='application/json',
            data={'accountnumb1': 1, 'amount': 10, 'accountnumb2': 2})
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'Account Balance': '990.00'})
        # check that balance has not changed
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        current_balance = account1.balance
        self.assertEqual(current_balance, 990)
        account2 = allofthem[1]
        current_balance = account2.balance
        self.assertEqual(current_balance, 510)

        # check if bankstatements were created
        all_statements = BankStatements.objects.filter()
        self.assertEqual(len(all_statements), 2)

        self.assertEqual(all_statements[0].transaction, 'sending 10 to 2')
        self.assertEqual(all_statements[0].balance, 990.00)
        self.assertEqual(all_statements[0].bankAccountId, account1)
        self.assertEqual(all_statements[1].transaction, 'received 10 from 1')
        self.assertEqual(all_statements[1].balance, 510.00)
        self.assertEqual(all_statements[1].bankAccountId, account2)
