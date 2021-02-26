from decimal import Decimal
from datetime import datetime
import json
import pydantic
from django.db import transaction
from django.http import HttpResponse, HttpRequest, Http404, HttpResponseBadRequest, JsonResponse
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.shortcuts import render

from .models import User, AccountType, BankAccount, EmployeeLevel, ApprovalStatus, BankStatements
from .common import make_user


MAX_REQUEST_LENGTH = 4096


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


def api_function(func):
    """
    This is a magic function which will automatically deserialize POST request data from JSON and serialize the response
    back to JSON. Additionally, it will typecheck the JSON object structure against the function's type annotations.
    Use it by @annotating your view functions with it.
    """
    gen_namespace = {name: NotImplemented for name in func.__annotations__}
    gen_namespace['__annotations__'] = func.__annotations__
    gen_namespace['Config'] = ApiGenConfig
    request_type = type(func.__name__ + '_args', (pydantic.BaseModel,), gen_namespace)

    def inner(request: HttpRequest, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseBadRequest("Must be a POST request")

        request_data = request.read(MAX_REQUEST_LENGTH + 1)
        if len(request_data) == MAX_REQUEST_LENGTH + 1:
            return HttpResponseBadRequest("Request too large")
        if len(request_data) == 0:
            request_data = b''

        try:
            request_data_dict = json.loads(request_data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponseBadRequest("Data encoding error")

        if not isinstance(request_data_dict, dict):
            # force an error in the next stanza
            request_data_dict = {'_': None}

        try:
            request_data_validated = request_type(**request_data_dict)
        except pydantic.ValidationError:
            return HttpResponseBadRequest("Data form error: expecting " + str(func.__annotations__))

        kwargs.update(request_data_validated.dict())
        result = func(request, *args, **kwargs)
        if result is None:
            result = {}
        if isinstance(result, HttpResponse):
            return result
        return JsonResponse(result, safe=False, json_dumps_params=dict(default=encode_extra))

    return inner


class ApiGenConfig:
    extra = pydantic.Extra.forbid
    validate_all = True


def encode_extra(thing):
    if isinstance(thing, Decimal):
        return str(thing)
    if isinstance(thing, datetime):
        return thing.isoformat()

    raise TypeError(f"Object of type {thing.__class__.__name__} is not serializable")


######
## actual views begin here
######

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
    return [{
        'id': pendingtransaction.id,
        'transaction': pendingtransaction.transaction,
        'balance': pendingtransaction.balance,
        'accountId': pendingtransaction.accountId.id,
        'description': pendingtransaction.description,
        'approval_status': pendingtransaction.approve_status
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


def tier1_users(request):

    if request.method == 'GET':
        return render(request, 'website/tier1_userPage.html')


def tier1_users_view(request):
    if request.method == 'POST':
        return render(request, 'website/tier1_viewPage.html')


def tier1_users_create(request):
    if request.method == 'POST':
        return render(request, 'website/tier1_createPage.html')

def tier1_users_authorize(request):
    if request.method == 'POST':
        return render(request, 'website/tier1_authorizePage.html')


@api_function
def bank_statement(request, account_id: int, month: int, year: int):
    user = current_user(request)
    try:
        BankAccount.objects.get(id=account_id, owner=user)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account") from exc

    transactions = BankStatements.objects \
        .filter(date__month=month, date__year=year, accountId=account_id, approval_status=ApprovalStatus.APPROVED) \
        .order_by("date")
    return [{
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
