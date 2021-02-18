from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from ..models import User, EmployeeLevel, BankAccount, DjangoUser, AccountType, BankStatements
from .. import views

def make_user(username,
              first_name='Firstname',
              last_name='Lastname',
              password='password',
              email='example@example.com',
              phone='0000000000',
              address='nowhere',
              employee_level=EmployeeLevel.CUSTOMER) -> User:
    """
    A function for quickly creating a user with a bunch of testing defaults set.
    """
    django_user = DjangoUser.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password)
    return User.objects.create(
        phone=phone,
        address=address,
        employee_level=employee_level,
        django_user=django_user)


class TestUserInformation(TestCase):
    def test_UserInformation(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        make_user('user1')
        make_user('user2')
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        client_user1 = Client()
        self.assertTrue(client_user1.login(username='user1', password='password'))
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
        req = client_admin.post(
            reverse(views.get_pending_bank_accounts),
            content_type='application/json',
            data={})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertIs(type(req_data), list)

        req = client_admin.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': req_data[0]['account'],
                  'approved': True})
        self.assertEqual(req.status_code, 200)

        req = client_admin.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': req_data[1]['account'],
                  'approved': True})
        # add money to accounts
        allofthem = BankAccount.objects.all()
        account1 = allofthem[0]
        account1.balance = 1000
        account1.save()
        account2 = allofthem[1]
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
        allStatements = BankStatements.objects.filter()
        self.assertEqual(len(allStatements), 2)

        self.assertEqual(allStatements[0].transaction, 'sending 10 to 2')
        self.assertEqual(allStatements[0].balance, 990.00)
        self.assertEqual(allStatements[0].bankAccountId, account1)
        self.assertEqual(allStatements[1].transaction, 'received 10 from 1')
        self.assertEqual(allStatements[1].balance, 510.00)
        self.assertEqual(allStatements[1].bankAccountId, account2)
