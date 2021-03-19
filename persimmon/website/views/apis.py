from decimal import Decimal
import hashlib

from django.contrib.auth import authenticate, login as django_login
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django import forms
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django.core import signing, mail

from . import current_user
from ..middleware import api_function
from ..models import BankAccount, EmployeeLevel, ApprovalStatus, Transaction, User, \
    Appointment, DjangoUser
from ..transaction_approval import check_approvals


def hashit(string):
    return hashlib.sha256(string.encode()).hexdigest()


def signit(string):
    return signing.Signer().sign(string)


def make_verification_code(*args, digits=6):
    return str(int(hashit(signit(''.join(hashit(arg) for arg in args))), 16) % (10 ** digits))


class CreateBankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ('type',)


def create_bank_account(request):
    user = current_user(request)

    if request.method == 'POST':
        form = CreateBankAccountForm(request.POST)
        if form.is_valid():
            form.instance.owner = user
            form.save()
            return TemplateResponse(request, 'pages/new_bank_account_success.html', {
                'account': form.instance,
            })
    else:
        form = CreateBankAccountForm()

    return TemplateResponse(request, 'pages/new_bank_account.html', {
        'form': form,
    })


class ApproveAccountForm(forms.Form):
    account_number = forms.IntegerField()
    approved = forms.BooleanField(required=False)
    back = forms.CharField()


@require_POST
def approve_bank_account(request):
    current_user(request, required_auth=EmployeeLevel.MANAGER)
    form = ApproveAccountForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Bad parameters")

    try:
        account = BankAccount.objects.get(
            id=form.cleaned_data['account_number'],
            approval_status=ApprovalStatus.PENDING)
    except BankAccount.DoesNotExist as exc:
        raise Http404("No such account pending approval") from exc

    account.approval_status = ApprovalStatus.APPROVED if form.cleaned_data['approved'] else ApprovalStatus.DECLINED
    account.save()

    return TemplateResponse(request, 'pages/account_approval_success.html', {
        'link': form.cleaned_data['back']
    })


class ApproveTransactionForm(forms.Form):
    transaction_id = forms.IntegerField()
    approved = forms.BooleanField(required=False)
    back = forms.CharField()


@transaction.atomic
@require_POST
def approve_transaction(request):
    user = current_user(request)
    form = ApproveTransactionForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Bad parameters")

    try:
        pendingtransaction = Transaction.objects.get(
            id=form.cleaned_data['transaction_id'],
            approval_status=ApprovalStatus.PENDING)
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


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('address', 'phone')


class DjangoUserForm(forms.ModelForm):
    class Meta:
        model = DjangoUser
        fields = ('first_name', 'last_name', 'email')


def edit_user(request, user_id):
    # load the users we're working with - the editor and the to-be-edited
    user_editor = current_user(request)
    try:
        user_edited = User.objects.get(id=user_id)
    except User.DoesNotExist as exc:
        raise Http404("No such user") from exc
    original_email = user_edited.email

    # check if editing this user is allowed, and furthermore,
    # whether we are allowed to bypass the verification steps.
    # we use editing_self to indicate whether verification is required
    if user_editor == user_edited:
        editing_self = True
    elif user_editor.employee_level >= EmployeeLevel.MANAGER:
        editing_self = False
    else:
        raise Http404("Cannot edit this user")

    # collect the post data into form objects
    form1 = UserForm(request.POST or None, instance=user_edited, prefix='persimmon')
    form2 = DjangoUserForm(request.POST or None, instance=user_edited.django_user, prefix='django')

    # handle the complex case: email verification required
    # we make two verification codes to certify the transition from one email to another
    # we ad-hoc add new fields to our form and re-collect the post data
    # if this is first submission, this just shows the user more fields to fill in
    # if this is the second submission, this retroactively accounts for the fact that we added these fields
    #
    # this logic could mayyyyybe live inside the clean() method
    # maybe it's even supposed to
    # but the logic with the verification fields being required sometimes but not others,
    # which can only be figured out after clean has happened? COMPLICATED
    if form1.is_valid() and form2.is_valid() and editing_self and form2.cleaned_data['email'] != original_email:
        # code 1 says username wants to change to new email, certified by old email
        verification_code_1 = make_verification_code(
            user_edited.username,
            form2.cleaned_data['email'],
            original_email)
        # code 2 says username wants to change to new email, certified by new email
        verification_code_2 = make_verification_code(
            user_edited.username,
            form2.cleaned_data['email'],
            form2.cleaned_data['email'])
        form2.fields['email_verification_1'] = forms.CharField()
        form2.fields['email_verification_2'] = forms.CharField()
        form2.full_clean()
        if not form2.is_valid():
            mail.send_mail(
                "Persimmon verification code",
                f"Here is the code 1 to update your email: {verification_code_1}",
                'noreply@persimmon.rhelmot.io',
                [original_email]
            )
            mail.send_mail(
                "Persimmon verification code",
                f"Here is the code 2 to update your email: {verification_code_2}",
                'noreply@persimmon.rhelmot.io',
                [form2.cleaned_data['email']]
            )
            form2.errors.clear()
            form2.add_error(
                'email_verification_1',
                'Please check both your emails and enter the codes we sent you here')
        elif form2.cleaned_data['email_verification_1'] != verification_code_1 or \
                form2.cleaned_data['email_verification_2'] != verification_code_2:
            form2.add_error('email_verification_1', 'Invalid codes')

    # if after all that checking the forms are valid, take any actions we need to
    if form1.is_valid() and form2.is_valid():
        form1.save()
        form2.save()
        form2.fields.pop('email_verification_1', None)
        form2.fields.pop('email_verification_2', None)
        form2.add_error(None, "Update success!")

    return TemplateResponse(request, 'pages/edit_user.html', {
        'form1': form1,
        'form2': form2,
    })


def get_my_info(request):
    user = current_user(request)
    return {
        'name': user.name,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
    }


@api_function
def get_all_info(request):
    return get_my_info(request)


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
def change_my_name(request, new_first: str, new_last: str):
    user = current_user(request)
    user.django_user.first_name = new_first
    user.django_user.last_name = new_last
    user.django_user.save()
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

@require_POST
def mobile_atm_handel(request):
    user = current_user(request, expect_not_logged_in=False)
    accountnumber = request.POST.get('acc')
    ammount = int(request.POST.get('number'))
    act = request.POST.get('act')
    ammount = abs(ammount)
    myaccount = BankAccount.objects.get(id=accountnumber)
    if myaccount.owner == user or user.employee_level>=EmployeeLevel.TELLER:
        if act == "True":
            if myaccount.balance >= ammount > 0:
                bankstatement = Transaction.objects.create(
                    description="Mobile ATM Debit",
                    account_add=myaccount,
                    account_subtract= None,
                    transaction=ammount,
                    approval_status=ApprovalStatus.PENDING)
                bankstatement.save()
                return TemplateResponse(request, 'pages/mobile_atm_success.html', {})
        bankstatement = Transaction.objects.create(
            description="Mobile ATM Credit",
            account_add=None,
            account_subtract=myaccount,
            transaction=ammount,
            approval_status=ApprovalStatus.PENDING)
        bankstatement.save()
        return TemplateResponse(request, 'pages/mobile_atm_success.html', {})

    return TemplateResponse(request, 'pages/mobile_atm_fail.html', {})


class UserLookupForm(forms.Form):
    search_term = forms.CharField()


def user_lookup(request):
    current_user(request, required_auth=EmployeeLevel.TELLER)
    form = UserLookupForm(request.POST)

    if form.is_valid():
        terms = form.cleaned_data['search_term'].split()
        query = User.objects
        for term in terms:
            query = query.filter(Q(django_user__first_name__icontains=term) |
                                 Q(django_user__last_name__icontains=term) |
                                 Q(django_user__email__icontains=term) |
                                 Q(django_user__username__icontains=term) |
                                 Q(phone__icontains=term) |
                                 Q(address__icontains=term))
    else:
        query = None

    return TemplateResponse(request, 'pages/user_lookup.html', {
        'form': form,
        'query': query,
    })
