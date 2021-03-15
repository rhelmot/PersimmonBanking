from decimal import Decimal

from django.contrib.auth import authenticate, login as django_login
from django.db import transaction
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django import forms
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from ..common import make_user
from . import current_user
from ..middleware import api_function
from ..models import AccountType, BankAccount, EmployeeLevel, ApprovalStatus, Transaction, User, \
    Appointment
from ..transaction_approval import check_approvals


@api_function
def create_bank_account(request, account_type: AccountType):
    user = current_user(request)
    account = BankAccount.objects.create(owner=user, type=account_type)
    return {'account': account.account_number}


class ApproveAccountForm(forms.Form):
    account_number = forms.IntegerField()
    approved = forms.BooleanField()
    back = forms.CharField()


@require_POST
def approve_bank_account(request):
    current_user(request, required_auth=EmployeeLevel.MANAGER)
    form = ApproveAccountForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Bad parameters")

    try:
        account = BankAccount.objects.get(id=form.cleaned_data['account_number'], approval_status=ApprovalStatus.PENDING)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account pending approval") from exc

    account.approval_status = ApprovalStatus.APPROVED if form.cleaned_data['approved'] else ApprovalStatus.DECLINED
    account.save()

    return TemplateResponse(request, 'pages/account_approval_success.html', {
        'link': form.cleaned_data['back']
    })


class ApproveTransactionForm(forms.Form):
    transaction_id = forms.IntegerField()
    approved = forms.BooleanField()
    back = forms.CharField()


@transaction.atomic
@require_POST
def approve_transaction(request):
    user = current_user(request)
    form = ApproveTransactionForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Bad parameters")

    try:
        pendingtransaction = Transaction.objects.get(id=form.cleaned_data['transaction_id'], approval_status=ApprovalStatus.PENDING)
    except Transaction.DoesNotExist:
        return HttpResponseNotFound("No such transaction pending approval")

    if not check_approvals(pendingtransaction, user):
        return HttpResponseForbidden("You cannot approve this transaction")

    if form.cleaned_data['approved']:
        pendingtransaction.add_approval(user)
        check_approvals(pendingtransaction, user)
    else:
        pendingtransaction.decline()

    return TemplateResponse(request, 'pages/transaction_approval_success.html', {
        'link': form.cleaned_data['back'],
    })


@api_function
def credit_debit_funds(request, account_id: int, transactionvalue: Decimal):
    user = current_user(request)

    if transactionvalue == 0:
        return {"error": "Zero-dollar transaction"}

    try:
        account = BankAccount.objects.get(id=account_id, owner=user, approval_status=ApprovalStatus.APPROVED)
    except BankAccount.DoesNotExist:
        return {"error": "No such account"}

    bankstatement = Transaction.objects.create(
        description="credit" if transactionvalue < 0 else "debit",
        account_add=account if transactionvalue > 0 else None,
        account_subtract=account if transactionvalue < 0 else None,
        transaction=abs(transactionvalue),
        approval_status=ApprovalStatus.PENDING)
    bankstatement.save()

    bankstatement.add_approval(user)
    check_approvals(bankstatement, user)
    return {}


@api_function
def get_pending_transactions(request, account_id: int):
    current_user(request, required_auth=EmployeeLevel.TELLER)
    try:
        account = BankAccount.objects.get(id=account_id)
    except BankAccount.DoesNotExist:
        return {"error": "No such account"}

    pendingtransactions = account.transactions.filter(approval_status=ApprovalStatus.PENDING)
    return [{
        'transactionid': creditdebit.id,
        'account_add': creditdebit.account_add.id if creditdebit.account_add is not None else None,
        'account_subtract': creditdebit.account_subtract.id if creditdebit.account_subtract is not None else None,
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
def login_status(request):
    return {"logged_in": request.user.is_authenticated}


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


@api_function
def transfer_funds(request, accountnumb1: int, amount: Decimal, accountnumb2: int):
    user = current_user(request)

    if amount <= 0:
        return {'error': 'Bad amount: must be positive'}

    with transaction.atomic():
        try:
            account1 = BankAccount.objects.get(id=accountnumb1, owner=user, approval_status=ApprovalStatus.APPROVED)
        except BankAccount.DoesNotExist:
            return {'error': 'account to debit does not exist or is not owned by user'}

        try:
            account2 = BankAccount.objects.get(id=accountnumb2, approval_status=ApprovalStatus.APPROVED)
        except BankAccount.DoesNotExist:
            return {'error': 'Account to credit does not exist'}

        trans = Transaction.objects.create(
            transaction=amount,
            account_add=account2,
            account_subtract=account1,
            description=f'transfer from {account1.account_number} to {account2.account_number}',
            approval_status=ApprovalStatus.PENDING,
        )

        trans.add_approval(user)
        check_approvals(trans, user)

        return {'status': 'pending' if trans.approval_status == ApprovalStatus.PENDING else 'complete'}


@api_function
def reset_password(request, email: str):
    current_user(request, expect_not_logged_in=True)
    try:
        User.objects.get(django_user__email=email)
    except User.DoesNotExist as exc:
        raise Http404("No such email in our databases...") from exc
    # TODO send an email here... lol
    return {}


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