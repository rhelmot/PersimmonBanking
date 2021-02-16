from datetime import datetime
from decimal import Decimal
import json
import pydantic
from django.db import transaction
from django.http import HttpResponse, HttpRequest, Http404, HttpResponseBadRequest, JsonResponse

from .models import User, AccountType, BankAccount, EmployeeLevel, ApprovalStatus, BankStatements

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
            account = BankAccount.objects.get(id=pendingtransaction.accountId, approval_status=ApprovalStatus.PENDING)
        except BankAccount.DoesNotExist as exc:
            raise Http404("No such account") from exc
        if pendingtransaction.transaction.startswith("-"):
            account.balance -= int(pendingtransaction.transaction[1])
            pendingtransaction.balance = account.balance
        else:
            account.balance += int(pendingtransaction.transaction[1])
            pendingtransaction.balance = account.balance
        account.save()
        now = datetime.now()
        pendingtransaction.date = now.strftime("%d %b")
        pendingtransaction.save()
    else:
        pendingtransaction.approve_status = ApprovalStatus.DECLINED
        now = datetime.now()
        pendingtransaction.date = now.strftime("%d %b")
        pendingtransaction.save()


@api_function
def credit_debit_funds(request, account_number: int, balance: Decimal):
    user = current_user(request)
    try:
        account = BankAccount.objects.get(id=account_number, owner=user, approval_status=ApprovalStatus.PENDING)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account") from exc
    if balance < 0:
        transactionbalance = str(balance)
    else:
        transactionbalance = "+" + str(balance)
    BankStatements.objects.create(accountId=account_number, transaction=transactionbalance, balance=account.balance)


@api_function
def get_pending_transactions(request, account_number: int):
    current_user(request, required_auth=EmployeeLevel.MANAGER)
    pendingtransactions = BankStatements.objects \
        .filter(accountId=account_number, approval_status=ApprovalStatus.PENDING)
    return [{
        'transactionid':credidebit.id,
        'accountid': credidebit.accountId,
        'transaction': credidebit.transaction,
        'balance': credidebit.balance,
        'approval_status': credidebit.approval_status,
    } for credidebit in pendingtransactions]