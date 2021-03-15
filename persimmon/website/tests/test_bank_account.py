from django.test import TestCase, Client
from django.urls import reverse

from ..views import apis, html_views
from ..models import EmployeeLevel, BankAccount, AccountType, ApprovalStatus
from ..common import make_user


class TestAccountWorkflow(TestCase):
    """
    Test the workflow for creating a bank account and accessing statements
    """

    def test_workflow(self):
        # setup database
        make_user('admin', employee_level=EmployeeLevel.ADMIN)
        user = make_user('user')
        user2 = make_user('user2')
        client_admin = Client()
        self.assertTrue(client_admin.login(username='admin', password='password'))
        client_user = Client()
        self.assertTrue(client_user.login(username='user', password='password'))
        client_user2 = Client()
        self.assertTrue(client_user2.login(username='user2', password='password'))

        # test that creating an invalid bank account errors
        req = client_user.post(
            reverse(apis.create_bank_account),
            content_type='application/json',
            data={"account_type": 9000})
        self.assertEqual(req.status_code, 400)

        # test that we can create bank accounts
        req = client_user.post(
            reverse(apis.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CHECKING})
        self.assertEqual(req.status_code, 200)
        req = client_user.post(
            reverse(apis.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.SAVINGS})
        self.assertEqual(req.status_code, 200)
        req = client_user.post(
            reverse(apis.create_bank_account),
            content_type='application/json',
            data={"account_type": AccountType.CREDIT})
        self.assertEqual(req.status_code, 200)

        # test that creating the accounts manipulates the database correctly
        all_accounts = list(BankAccount.objects.all())
        self.assertEqual(len(all_accounts), 3)
        self.assertTrue(all(x.approval_status == ApprovalStatus.PENDING for x in all_accounts))

        # test that the accounts do not appear to another user
        req = client_user2.get(reverse(html_views.account_overview_page, args=(user2.id,)))
        for account in all_accounts:
            self.assertNotIn(account.account_number, req.content.decode())

        # test that the accounts appear as pending
        req = client_user.get(reverse(html_views.account_overview_page, args=(user.id,)))
        for account in all_accounts:
            self.assertIn(account.account_number, req.content.decode())
        self.assertIn('Pending', req.content.decode())

        # test that the user cannot access the admin functions
        req = client_user.get(reverse(html_views.employee_page))
        self.assertEqual(req.status_code, 404)
        req = client_user.post(reverse(apis.approve_bank_account))
        self.assertEqual(req.status_code, 404)

        # test the admin function for viewing pending accounts
        req = client_admin.get(reverse(html_views.employee_page))
        for account in all_accounts:
            self.assertIn(account.account_number, req.content.decode())

        # test approving the accounts
        for account in all_accounts:
            req = client_admin.post(reverse(apis.approve_bank_account),
                                    data={'account_number': account.id,
                                          'approved': True,
                                          'back': 'foo'})
            # print(req_data)
            self.assertEqual(req.status_code, 200)

        # test that we can't approve something twice
        req = client_admin.post(reverse(apis.approve_bank_account),
                                data={'account_number': all_accounts[0].id,
                                      'approved': True,
                                      'back': 'foo'})
        # print(req_data)
        self.assertEqual(req.status_code, 404)

        # test that the requests no longer appear on the admin end
        req = client_admin.get(reverse(html_views.employee_page))
        for account in all_accounts:
            self.assertNotIn(account.account_number, req.content.decode())

        # test that now the approved accounts appear to the user
        req = client_user.get(reverse(html_views.account_overview_page, args=(user.id,)))
        for account in all_accounts:
            self.assertIn(account.account_number, req.content.decode())
        self.assertNotIn('Pending', req.content.decode())

        # PHEW

    def test_bank_statements(self):
        # setup database
        user = make_user('user')
        make_user('user2')
        client_user2 = Client()
        self.assertTrue(client_user2.login(username='user2', password='password'))
        account = BankAccount.objects.create(owner=user, approval_status=ApprovalStatus.APPROVED,
                                             type=AccountType.CHECKING)

        # test that you can't get entries for other users
        req = client_user2.get(reverse(html_views.statement_page, args=(account.id,)))
        self.assertEqual(req.status_code, 404)
