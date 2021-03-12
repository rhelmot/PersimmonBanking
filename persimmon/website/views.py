from decimal import Decimal
from datetime import datetime

import asyncio
from django.db import transaction
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django import forms, urls
from django.template.response import TemplateResponse

from hfc.fabric import Client
from hfc.fabric_network.gateway import Gateway

from .models import User, AccountType, BankAccount, EmployeeLevel, ApprovalStatus, BankStatements
from .common import make_user
from .middleware import api_function



def current_user(request, required_auth=EmployeeLevel.CUSTOMER, expect_not_logged_in=False):
    if expect_not_logged_in:
        if not request.user.is_authenticated:
            return None
        raise Http404("API unavailable to current authentication")

    if not request.user.is_authenticated:
        raise Http404("API unavailable to current authentication")

    user = User.objects.get(django_user=request.user)
    if not user.check_level(required_auth):
        raise Http404("API unavailable to current authentication")
    return user


# checks if user with username has same employeelevel as level
def security_check(request, myusername, level):
    try:
        user = User.objects.get(username=myusername)
    except User.DoesNotExist as exc:
        raise Http404("epic fail user does not exist") from exc

    if not user.check_level(level):
        return HttpResponse("fail this user does not have required permissions")

    return HttpResponse("success this user match the required permissions")


# index for website/ to check if url views are working
def index(request):
    return HttpResponse("Hello world")


@api_function
def create_user_account(request, username: str, first_name: str,
                        last_name: str, password: str, email: str,
                        phone: str, address: str):
    current_user(request, expect_not_logged_in=True)
    new_user = make_user(username=username,
                         first_name=first_name,
                         last_name=last_name,
                         password=password,
                         email=email,
                         phone=phone,
                         address=address)
    new_user.save()


@api_function
def create_bank_account(request, account_type: AccountType):
    user = current_user(request)
    account = BankAccount.objects.create(owner=user, type=account_type)
    return {'account': account.account_number}


@api_function
def get_pending_bank_accounts(request):
    current_user(request, required_auth=EmployeeLevel.MANAGER)
    accounts = BankAccount.objects.filter(approval_status=ApprovalStatus.PENDING)
    return [{
        'account': account.account_number,
        'owner': account.owner_id,
        'type': account.type
    } for account in accounts]


@api_function
def approve_bank_account(request, account_number: int, approved: bool):
    current_user(request, required_auth=EmployeeLevel.MANAGER)
    try:
        account = BankAccount.objects.get(id=account_number, approval_status=ApprovalStatus.PENDING)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account pending approval") from exc

    account.approval_status = ApprovalStatus.APPROVED if approved else ApprovalStatus.DECLINED
    account.save()


@api_function
def get_my_accounts(request):
    user = current_user(request)
    accounts = BankAccount.objects.filter(owner=user).exclude(approval_status=ApprovalStatus.DECLINED)
    return [{
        'account': account.account_number,
        'type': account.type,
        'balance': account.balance,
        'approval_status': account.approval_status,
    } for account in accounts]


@transaction.atomic
@api_function
def approve_credit_debit_funds(request, transaction_id: int, approved: bool):
    current_user(request, required_auth=EmployeeLevel.TELLER)
    try:
        pendingtransaction = BankStatements.objects.get(id=transaction_id, approval_status=ApprovalStatus.PENDING)
    except BankStatements.DoesNotExist as exc:
        raise Http404("No such transaction pending approval") from exc
    if approved:
        pendingtransaction.approve_status = ApprovalStatus.APPROVED
        try:
            account = BankAccount.objects.get(id=pendingtransaction.accountId.id,
                                              approval_status=ApprovalStatus.PENDING)
        except BankAccount.DoesNotExist as exc:
            raise Http404("No such account") from exc
        account.balance += pendingtransaction.transaction
        pendingtransaction.balance = account.balance
        account.save()
    else:
        pendingtransaction.approve_status = ApprovalStatus.DECLINED
    pendingtransaction.date = datetime.now()
    pendingtransaction.save()
    bank_statement = pendingtransaction
    bank_statement_date_time = pendingtransaction.date.strftime("%m/%d/%Y, %H:%M:%S")
    create_bank_statement_to_blockchain(request, bank_statement.id, bank_statement_date_time
                                                  , bank_statement.transaction,bank_statement.balance
                                                  , bank_statement.accountId.id, bank_statement.description)
    return [{
        'id': pendingtransaction.id,
        'transaction': pendingtransaction.transaction,
        'date': bank_statement_date_time,
        'balance': pendingtransaction.balance,
        'accountId': pendingtransaction.accountId.id,
        'description': pendingtransaction.description,
        'approval_status': pendingtransaction.approve_status,
    }]


@api_function
def credit_debit_funds(request, account_id: int, transactionvalue: Decimal):
    user = current_user(request)
    try:
        account = BankAccount.objects.get(id=account_id, owner=user, approval_status=ApprovalStatus.PENDING)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account") from exc
    bankstatement = BankStatements.objects.create(accountId=account, transaction=transactionvalue)
    if transactionvalue < 0:
        bankstatement.description = "credit"
    else:
        bankstatement.description = "debit"
    bankstatement.save()


@api_function
def get_pending_transactions(request, account_id: int):
    current_user(request, required_auth=EmployeeLevel.MANAGER)
    try:
        account = BankAccount.objects.get(id=account_id)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account") from exc
    pendingtransactions = BankStatements.objects \
        .filter(accountId=account, approval_status=ApprovalStatus.PENDING)
    return [{
        'transactionid': creditdebit.id,
        'accountId': creditdebit.accountId.id,
        'transaction': creditdebit.transaction,
        'description': creditdebit.description,
        'approval_status': creditdebit.approval_status,
    } for creditdebit in pendingtransactions]


def create_bank_statement_to_blockchain(request,transaction_id: int, date: str, transaction: Decimal, balance: Decimal
                                        , account_id: int, description: str):
    try:
        loop = asyncio.get_event_loop()
        cli = \
            Client(net_profile="/home/xiao/persimmon/fabric-samples-release-1.4test2/basic-network/connectionnew.json")
        org1_admin = cli.get_user(org_name='Org1', name='Admin')

        new_gateway = Gateway()  # Creates a new gateway instance
        options = {'wallet': ''}
        loop.run_until_complete(
            new_gateway
                .connect('/home/xiao/persimmon/fabric-samples-release-1.4test2/basic-network/connectionnew.json',
                                options))
        new_network = loop.run_until_complete(new_gateway.get_network('mychannel', org1_admin))
        new_contract = new_network.get_contract('bankcode')
        transaction_status = "approved"
        transaction_id = str(transaction_id)
        transaction = str(transaction)
        balance = str(balance)
        account_id = str(account_id)
        arg = [transaction_id,date, transaction, balance, account_id, description, transaction_status]
        loop.run_until_complete(new_contract.submit_transaction('mychannel', arg, org1_admin))
        raise Http404("create bank statement fail")
    except Http404 as exc:
        print(exc)


@api_function
def get_bank_statement_from_blockchain(request, account_id: int):
    try:
        user = current_user(request)
        BankAccount.objects.get(id=account_id, owner=user)
        loop = asyncio.get_event_loop()
        cli = Client(net_profile="/home/xiao/persimmon/fabric-samples-release-1.4test2/basic-network/connectionnew.json")
        org1_admin = cli.get_user(org_name='Org1', name='Admin')
        account_id = str(account_id)
        args = [account_id]
        new_gateway = Gateway()  # Creates a new gateway instance
        options = {'wallet': ''}
        loop.run_until_complete(
            new_gateway.connect('/home/xiao/persimmon/fabric-samples-release-1.4test2/basic-network/connectionnew.json',
                                options))
        new_network = loop.run_until_complete(new_gateway.get_network('mychannel', org1_admin))
        new_contract = new_network.get_contract('bankcode')
        response = loop.run_until_complete(new_contract.evaluate_transaction('mychannel', args, org1_admin))
        raise Http404("get bank statement fail")
    except Http404 as exc:
        print(exc)
    print(response)
    return response


@api_function
def persimmon_login(request, username: str, password: str):
    current_user(request, expect_not_logged_in=True)
    django_user = authenticate(request, username=username, password=password)
    if django_user is None:
        return {"error": "could not authenticate"}

    django_login(request, django_user)
    return {}


@api_function
def persimmon_logout(request):
    current_user(request)
    django_logout(request)
    return {}


@api_function
def login_status(request):
    return {"logged_in": request.user.is_authenticated}

@api_function
def bank_statement(request, account_id: int, month: int, year: int):
    user = current_user(request)
    try:
        BankAccount.objects.get(id=account_id, owner=user)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account") from exc

    transactions = BankStatements.objects\
        .filter(date__month=month, date__year=year, accountId=account_id, approval_status=ApprovalStatus.APPROVED)\
        .order_by("date")
    return [ {
        'timestamp': trans.date,
        'transaction': trans.transaction,
        'balance': trans.balance,
        'description': trans.description,
    } for trans in transactions]

@api_function
def get_all_info(request):
    user = current_user(request)
    return {
        'name': user.name,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
    }


@api_function
def change_my_email(request, new_email: str):
    user = current_user(request)
    user.change_email(new_email)
    return {
        'my new email': user.email
    }


@api_function
def change_my_phone(request, new_phone: str):
    user = current_user(request)
    user.phone = new_phone
    user.save()
    return {
        'my new phone': user.phone
    }


@api_function
def change_my_address(request, new_address: str):
    user = current_user(request)
    user.address = new_address
    user.save()
    return {
        'my new address': user.address
    }


# transfer amount from the balance of bankaccount with acountnumb1 id
@api_function
def transfer_funds(request, accountnumb1: int, amount: Decimal, accountnumb2: int):
    with transaction.atomic():
        user = current_user(request)
        account1 = BankAccount.objects.filter(id=accountnumb1).exclude(approval_status=ApprovalStatus.DECLINED)
        if len(account1) == 1 and account1[0].owner.django_user.username == user.username:
            if account1[0].balance < amount or amount <= 0:
                return {
                    'error': 'error insufficient funds'
                }
            account2 = BankAccount.objects.filter(id=accountnumb2).exclude(approval_status=ApprovalStatus.DECLINED)
            if len(account2) == 1:
                account1[0].balance = account1[0].balance-amount
                account1[0].save()
                acc1statement = BankStatements.objects.create(
                    transaction=-1*amount,
                    balance=account1[0].balance,
                    accountId=account1[0],
                    description='sent '+str(amount)+' to '+str(accountnumb2),
                    approval_status=ApprovalStatus.APPROVED

                )
                acc1statement.save()
                account2[0].balance = account2[0].balance+amount
                account2[0].save()
                acc2statement = BankStatements.objects.create(

                    transaction=amount,
                    balance=account2[0].balance,
                    accountId=account2[0],
                    description='received '+str(amount)+' from '+str(accountnumb1),
                    approval_status=ApprovalStatus.APPROVED
                )
                acc2statement.save()
                return {
                    'Account Balance': account1[0].balance
                }

            return {
                'error': 'account number 2 does not exit'
            }
        return {
            'error': 'account to debt does not exist or is not owned by user'
        }

@api_function
def reset_password(request, email: str):
    current_user(request, expect_not_logged_in=True)
    try:
        User.objects.get(django_user__email=email)
    except User.DoesNotExist as exc:
        raise Http404("No such email in our databases...") from exc
    # TODO send an email here... lol
    return {}

class ResetPasswordForm(forms.Form):
    email = forms.CharField(max_length=200)

def reset_password_page(request):
    current_user(request, expect_not_logged_in=True)

    return TemplateResponse(request, 'pages/reset_password.html', {
        'form': ResetPasswordForm(),
        'api': urls.reverse(reset_password),
        'success': urls.reverse(reset_password_sent)
    })

def reset_password_sent(request):
    current_user(request, expect_not_logged_in=True)

    return TemplateResponse(request, 'pages/reset_password_sent.html', {})
