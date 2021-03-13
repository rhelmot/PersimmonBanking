from decimal import Decimal
from datetime import datetime

from bootstrap_datepicker_plus import DateTimePickerInput
from django.db import transaction

from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.core.validators import RegexValidator
from django import forms, urls
from django.template.response import TemplateResponse

from .models import User, AccountType, BankAccount, EmployeeLevel, ApprovalStatus, BankStatements, DjangoUser,\
    Appointment
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
    print("created")
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
def get_accounts(request):
    return get_my_accounts(request)


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


def logout(request):
    persimmon_logout(request)
    return HttpResponse("you have been logged out")


@api_function
def login_status(request):
    return {"logged_in": request.user.is_authenticated}


@api_function
def bank_statement(request, account_id: int, month: int, year: int):
    return get_bank_statement(request, account_id, month, year)


def get_bank_statement(request, account_id: int, month: int, year: int):
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
                account1[0].balance = account1[0].balance - amount
                account1[0].save()
                acc1statement = BankStatements.objects.create(
                    transaction=-1 * amount,
                    balance=account1[0].balance,
                    accountId=account1[0],
                    description='sent ' + str(amount) + ' to ' + str(accountnumb2),
                    approval_status=ApprovalStatus.APPROVED

                )
                acc1statement.save()
                account2[0].balance = account2[0].balance + amount
                account2[0].save()
                acc2statement = BankStatements.objects.create(

                    transaction=amount,
                    balance=account2[0].balance,
                    accountId=account2[0],
                    description='received ' + str(amount) + ' from ' + str(accountnumb1),
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


@api_function
def schedule(request, time: str):
    user = current_user(request, expect_not_logged_in=False)
    for empteller in User.objects.all().filter(employee_level=1):
        if not Appointment.objects.filter(employee=empteller, time=time):
            newapp = Appointment.objects.create(
                employee=empteller,
                customer=user,
                time=time
            )
            newapp.save()
            return {}
    return {"error": "No employees available at this time"}


class ScheduleAppointment(forms.Form):
    time = forms.DateTimeField(widget=DateTimePickerInput(options={
        "stepping": "15",
        "useCurrent": True,
        "sideBySide": True,
        "daysOfWeekDisabled": [0, 6],
        "disabledHours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 18, 19, 20, 21, 22, 23, 24],
        "enabledHours": [9, 10, 11, 12, 15, 16]
    }))


def schedule_appointment_page(request):
    return TemplateResponse(request, 'pages/schedule_appointment.html', {
        'form': ScheduleAppointment(),
        'api': urls.reverse(schedule),
        'success': urls.reverse(schedule_success)
    })


def schedule_success(request):
    current_user(request, expect_not_logged_in=False)
    return TemplateResponse(request, 'pages/appointmentbooked.html', {})


def check_create_account(request, first_name: str, last_name: str, email: str, my_user_name: str,
                         phone: str, address: str, password: str, confirm_password: str):
    current_user(request, expect_not_logged_in=True)
    check = DjangoUser.objects.filter(username=my_user_name)
    if len(check) > 0:
        return {'error': "username unavailable"}
    check = DjangoUser.objects.filter(email=email)
    if len(check) > 0:
        return {'error': "email unavailable"}
    res = False
    for letter in password:
        if letter.isupper():
            res = True
            break
    if not res:
        return{'error': "password does not contain an capital letter"}

    if len(password) < 8:
        return {'error': "password not long enough"}
    res = False

    for letter in password:
        if letter in ('!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '<', '>', '?'):
            res = True
            break
    if not res:
        return {'error': "password does not contain a special character such as !, @, #, etc"}
    res = False
    for letter in password:
        if letter.isnumeric():
            res = True
            break
    if not res:
        return {'error': "password does not contain a number"}

    if password != confirm_password:
        return{'error': "passwords does not match"}

    new_user = make_user(username=my_user_name,
                         first_name=first_name,
                         last_name=last_name,
                         password=password,
                         email=email,
                         phone=phone,
                         address=address)
    new_user.save()
    return {}


    # TODO send an email here... lol


class CreateUserForm(forms.Form):
    first_name = forms.CharField(label='First name',
                                 error_messages={'required': 'Please enter your First name'},
                                 max_length=30, required=True)
    last_name = forms.CharField(label='Last Name',
                                error_messages={'required': 'Please enter your Last name'},
                                max_length=30, required=True)
    email = forms.EmailField()
    myusername = forms.CharField(label='Username',
                               error_messages={'required': 'Please enter a Username'},
                               max_length=30, required=True)
    phone = forms.CharField(label='Phone Number', max_length=12,
                            error_messages={'incomplete': 'Enter a phone number.'},
                            validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')]
                            , required=True)
    address = forms.CharField(label='address', max_length=50, required=True)
    password = forms.CharField(label='Password', max_length=18, required=True)
    confirm_password = forms.CharField(label='Confirm Password', max_length=18, required=True)


def create_user_page(request):
    current_user(request, expect_not_logged_in=True)
    return TemplateResponse(request, 'pages/create_account.html', {
        'form': CreateUserForm(),
        'api': urls.reverse(check_create_account),
        'success': urls.reverse(create_user_success),

    })


def create_user_success(request):
    current_user(request, expect_not_logged_in=True)
    return TemplateResponse(request, 'pages/create_account_success.html', {})


def account_overview_page(request):
    usr = current_user(request, expect_not_logged_in=False)
    acc = get_my_accounts(request)
    number = 0
    while number < len(acc):
        if acc[number]['approval_status'] == 0:
            acc.pop(number)
            number = number-1
        if acc[number]['type'] == 0:
            acc[number]['type'] = 'Checking'
        if acc[number]['type'] == 1:
            acc[number]['type'] = 'Savings'
        if acc[number]['type'] == 2:
            acc[number]['type'] = 'Credit'
        number = number+1
    mydict = {"name": usr.name, 'ls': acc}
    return TemplateResponse(request, 'pages/account_overview.html', mydict)


def temp_statement_page(request, number):
    current_user(request, expect_not_logged_in=False)
    statement = "this is where I would show statements for account " +str(number)
    return HttpResponse(statement)
