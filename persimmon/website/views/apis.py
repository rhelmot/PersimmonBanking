from decimal import Decimal
import hashlib
import random
import os
import io

from PIL import Image, ImageDraw, ImageFont
from num2words import num2words

from django.contrib.auth import authenticate, login as django_login
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django import forms
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core import signing, mail
from sms import send_sms

from . import current_user
from ..middleware import api_function
from ..models import BankAccount, EmployeeLevel, ApprovalStatus, Transaction, User, DjangoUser
from ..transaction_approval import check_approvals

# phone number is +13236949222


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


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


def persimmon_login(request):
    current_user(request, expect_not_logged_in=True)
    form = LoginForm(request.POST or None)
    django_user = persimmon_user = None

    # pass 1: check authentication
    if form.is_valid():
        django_user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'])
        if django_user is None:
            form.add_error(None, "Username or password is incorrect")

        try:
            persimmon_user = User.objects.get(django_user=django_user)
        except User.DoesNotExist:
            form.add_error(None, "Username or password is incorrect")

    # pass 2: check otp
    if form.is_valid():
        # if we get this far and we need to render the form again don't wipe the password and display the otp field
        form.fields['password'].widget.render_value = True
        form.fields['login_code'] = forms.CharField()
        form.full_clean()

        # if the form is no longer valid no otp was not entered, generate and send it
        if not form.is_valid():
            form.errors.clear()
            form.add_error(None, "Please enter the code we just sent to your phone")

            otp = '%06d' % random.randint(0, 999999)
            request.session['sent_otp'] = otp
            request.session['username'] = django_user.username

            send_sms(
                f'Your Persimmon login code is {otp}',
                originator=settings.SMS_SENDER,
                recipients=[persimmon_user.phone])

        # if the otp or cached username mismatch then error
        elif form.cleaned_data['login_code'] != request.session.get('sent_otp', None) or \
                form.cleaned_data['username'] != request.session.get('username', None):
            form.add_error('login_code', 'Invalid code')

        # got em
        else:
            django_login(request, django_user)
            return TemplateResponse(request, 'pages/login_success.html', {})

    return TemplateResponse(request, 'pages/login.html', {
        'form': form,
    })


@api_function
def otp_check(request, otp: str):
    current_user(request, expect_not_logged_in=True)
    username = request.session.get('username', None)
    sent_otp = request.session.get('sent_otp', None)
    if otp != sent_otp:
        return {'error': 'Wrong OTP'}

    user = User.objects.get(django_user__username=username)
    django_login(request, user.django_user)
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


arial_path = os.path.join(os.path.dirname(__file__), '../static/arial.ttf')
arial30 = ImageFont.truetype(arial_path, 30)
arial15 = ImageFont.truetype(arial_path, 15)


def check_image(request, tid):
    user = current_user(request)
    filter_owner = {'account_subtract__owner': user} if user.employee_level == EmployeeLevel.CUSTOMER else {}
    try:
        trans = Transaction.objects.exclude(balance_subtract=None).get(id=tid, **filter_owner)
        if trans.check_recipient is None:
            raise Transaction.DoesNotExist
    except Transaction.DoesNotExist as exc:
        raise Http404("Cannot view check") from exc

    payer_lines = [x.strip() for x in trans.account_subtract.owner.address.replace('\r', '').split(',')]
    payer_lines.insert(0, trans.account_subtract.owner.name)
    amount_text = f'{num2words(int(trans.transaction))} dollars and '\
                  f'{num2words(int(trans.transaction * 100) % 100)} cents'

    img_path = os.path.join(os.path.dirname(__file__), '../static/checkbg.jpg')
    img = Image.open(img_path)
    imgm = ImageDraw.Draw(img)
    stroke = {'fill': (0, 0, 0), 'stroke_fill': (200, 200, 200), 'stroke_width': 2}
    imgm.text((100, 80), f"Persimmon Banking #{tid}", font=arial30, **stroke)
    imgm.text((1000, 80), f'${trans.transaction}', font=arial30, **stroke)
    imgm.text((100, 130), "Pay", font=arial15, **stroke)
    imgm.text((100, 150), amount_text, font=arial30, **stroke)
    imgm.text((100, 190), "to the order of", font=arial15, **stroke)
    imgm.text((100, 210), trans.check_recipient.replace('\r', ''), font=arial30, **stroke)
    imgm.text((800, 300), "Pay from " + trans.account_subtract.account_number, font=arial15, **stroke)
    imgm.text((800, 320), '\n'.join(payer_lines), font=arial30, **stroke)

    stream = io.BytesIO()
    fmt = Image.registered_extensions()['.png']
    img.save(stream, fmt)
    return HttpResponse(stream.getvalue(), content_type='image/png')
