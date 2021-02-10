from decimal import Decimal
import json
import pydantic
from django.http import HttpResponse, HttpRequest, Http404, HttpResponseBadRequest, JsonResponse

from .models import User, AccountType, BankAccount, EmployeeLevel, ApprovalStatus

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

#checks if user with username has same employeelevel as level
def security_check(request, myusername, level):
    try:
        user = User.objects.get(username=myusername)
    except User.DoesNotExist as exc:
        raise Http404("epic fail user does not exist") from exc

    if not user.check_level(level):
        return HttpResponse("fail this user does not have required permissions")

    return HttpResponse("success this user match the required permissions")

#index for website/ to check if url views are working
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

@api_function
def get_my_address(request):
    user = current_user(request)
    return [{
        'my address': user.address
    }]

@api_function
def change_my_address(request, new_address: str):
    user = current_user(request)
    user.address = new_address
    user.save()
    return [{
        'my new address': user.address
    }]


#transfer amount from the balance of bankaccount with acountnumb1 id
@api_function
def transfer_funds(request, accountnumb1: int, amount: Decimal, accountnumb2: int):
    user = current_user(request)
    account1 = BankAccount.objects.filter(owner=user, id=accountnumb1).exclude(approval_status=ApprovalStatus.DECLINED)
    if len(account1)== 1:
        if account1[0].balance < amount:
            return [{
                'error':'error insufficient funds'
            }]
        else:
            account2= BankAccount.objects.filter(id=accountnumb2).exclude(approval_status=ApprovalStatus.DECLINED)
            if len(account2)==1:
                account1[0].balance = account1[0].balance-amount
                account2[0].balance = account2[0].balance+amount
                account1[0].save()
                account2[0].save()
                return [{
                    'Account Balance': account1[0].balance
                }]
            else:
                return [{
                    'error': 'account number 2 does not exit'
                }]
    else:
        return [{
            'error': 'account to debt does not exist or is not owned by user'
        }]







