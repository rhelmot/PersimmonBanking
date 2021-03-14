import datetime

from django.test import TestCase, Client
from django.urls import reverse

from ..models import EmployeeLevel, BankAccount, AccountType, ApprovalStatus, BankStatements
from .. import views
from ..common import make_user


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

        # test that creating an invalid bank account errors
        req = client_user.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": 9000})
        self.assertEqual(req.status_code, 400)

        # test that we can create bank accounts
        req = client_user.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CHECKING})
        self.assertEqual(req.status_code, 200)
        req = client_user.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.SAVINGS})
        self.assertEqual(req.status_code, 200)
        req = client_user.post(
            reverse(views.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CREDIT})
        self.assertEqual(req.status_code, 200)

        # test that creating the accounts manipulates the database correctly
        all_accounts = list(BankAccount.objects.all())
        self.assertEqual(len(all_accounts), 3)
        self.assertTrue(all(x.approval_status == ApprovalStatus.PENDING for x in all_accounts))

        # test that the accounts do not appear to another user
        req = client_admin.post(
            reverse(views.get_accounts),
            content_type='application/json',
            data={})
        req_data = req.json()
        self.assertIs(type(req_data), list)
        self.assertEqual(len(req_data), 0)

        # test that the accounts appear as pending
        req = client_user.post(
            reverse(views.get_accounts),
            content_type='application/json',
            data={})
        req_data = req.json()
        self.assertIs(type(req_data), list)
        self.assertEqual(len(req_data), 3)
        self.assertTrue(all(acct['approval_status'] == ApprovalStatus.PENDING for acct in req_data))

        # test that the user cannot access the admin functions
        req = client_user.post(
            reverse(views.get_pending_bank_accounts),
            content_type='application/json',
            data={})
        self.assertEqual(req.status_code, 404)
        req = client_user.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': 0, 'approved': True})
        self.assertEqual(req.status_code, 404)

        # test the admin function for viewing pending accounts
        req = client_admin.post(
            reverse(views.get_pending_bank_accounts),
            content_type='application/json',
            data={})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertIs(type(req_data), list)
        self.assertEqual(len(req_data), 3)

        # test approving the accounts
        req = client_admin.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': req_data[0]['account'],
                  'approved': True})
        # print(req_data)
        self.assertEqual(req.status_code, 200)
        req = client_admin.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': req_data[1]['account'],
                  'approved': True})
        self.assertEqual(req.status_code, 200)
        req = client_admin.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': req_data[2]['account'],
                  'approved': False})
        self.assertEqual(req.status_code, 200)

        # test that we can't approve something twice
        req = client_admin.post(
            reverse(views.approve_bank_account),
            content_type='application/json',
            data={'account_number': req_data[2]['account'],
                  'approved': True})
        self.assertEqual(req.status_code, 404)

        # test that the requests no longer appear on the admin end
        req = client_admin.post(
            reverse(views.get_pending_bank_accounts),
            content_type='application/json',
            data={})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertIs(type(req_data), list)
        self.assertEqual(len(req_data), 0)

        # test that now the approved accounts appear to the user
        req = client_user.post(
            reverse(views.get_accounts),
            content_type='application/json',
            data={})
        req_data = req.json()
        self.assertIs(type(req_data), list)
        self.assertEqual(len(req_data), 2)
        self.assertTrue(all(acct['approval_status'] == ApprovalStatus.APPROVED for acct in req_data))

        # PHEW

    def test_bank_statements(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        user = make_user('user')
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))
        account = BankAccount.objects.create(owner=user, approval_status=ApprovalStatus.APPROVED,
                                   type=AccountType.CHECKING)

        def create_transaction(balance, description, date, approved):
            BankStatements.objects.create(
                accountId=account,
                transaction=1,
                balance=balance,
                description=description,
                date=date,
                approval_status=ApprovalStatus.APPROVED if approved else ApprovalStatus.PENDING)

        # add transactions to database
        create_transaction(0, "0", datetime.date(2020, 2, 1), True)
        create_transaction(1, "1", datetime.date(2021, 1, 1), True)
        create_transaction(2, "2", datetime.date(2021, 2, 1), True)
        create_transaction(2, "X", datetime.date(2021, 2, 1), False)
        create_transaction(3, "3", datetime.date(2021, 3, 1), True)

        # test that we get back only relevant entries
        req = client_user.post(
            reverse(views.bank_statement),
            content_type='application/json',
            data={"account_id": account.id, "month": 2, "year": 2021})
        self.assertEqual(req.status_code, 200)
        req_data = req.json()
        self.assertIs(type(req_data), list)
        self.assertEqual(len(req_data), 1)
        self.assertEqual(req_data[0]["description"], "2")

        # test that you can't get entries for other users
        req = client_admin.post(
            reverse(views.bank_statement),
            content_type='application/json',
            data={"account_id": account.id, "month": 2, "year": 2021})
        self.assertEqual(req.status_code, 404)
