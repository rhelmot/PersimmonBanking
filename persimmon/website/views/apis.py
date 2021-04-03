import hashlib
import random
import os
import io

from PIL import Image, ImageDraw, ImageFont
from num2words import num2words

from django.core.validators import RegexValidator
from django.contrib.auth import authenticate, login as django_login
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django import forms
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core import signing, mail
from sms import send_sms
try:
    from hfc.fabric import Client
    from hfc.fabric_network.gateway import Gateway
except ImportError:
    Client = Gateway = None

from . import current_user
from ..models import BankAccount, EmployeeLevel, ApprovalStatus, Transaction, User, DjangoUser, UserEditRequest, \
    SignInHistory
from ..transaction_approval import check_approvals
from ..common import event_loop


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
        account = BankAccount.objects.select_for_update().get(
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
    approved = forms.BooleanField(required=False)


@transaction.atomic
def approve_transaction_page(request, tid):
    user = current_user(request)
    form = ApproveTransactionForm(request.POST or None)
    try:
        trans = Transaction.objects.select_for_update().get(id=tid, approval_status=ApprovalStatus.PENDING)
        if not check_approvals(trans, user):
            raise Transaction.DoesNotExist
    except Transaction.DoesNotExist as exc:
        raise Http404("No such transaction") from exc

    if form.is_valid():
        verification_code = make_verification_code(
            'approve_transaction',
            str(form.cleaned_data['approved']),
            user.username,
            str(tid))
        form.fields['email_verification'] = forms.CharField()
        form.full_clean()
        if not form.is_valid():
            mail.send_mail(
                "Persimmon verification code",
                f"Here is the code to verify your transaction approval: {verification_code}",
                settings.EMAIL_SENDER,
                [user.email]
            )
            form.errors.clear()
            form.add_error(
                'email_verification',
                'Please check your email and enter the code we sent you here')
        elif form.cleaned_data['email_verification'] != verification_code:
            form.add_error('email_verification', 'Invalid code')
        else:
            if form.cleaned_data['approved']:
                trans.add_approval(user)
                check_approvals(trans, user)
            else:
                trans.decline()

            return TemplateResponse(request, 'pages/transaction_approval_success.html', {
                'approved': form.cleaned_data['approved'],
                'link': request.GET.get("back", None)
            })

    return TemplateResponse(request, 'pages/transaction_approval.html', {
        'transaction': trans,
        'form': form,
    })


def get_bank_statement_from_blockchain(request, account_id):
    if not settings.BLOCKCHAIN_CONNECTION:
        raise Http404("Blockchain is disconnected")

    user = current_user(request)
    if user.employee_level == EmployeeLevel.CUSTOMER and \
            not BankAccount.objects.filter(id=account_id, owner=user).exists():
        raise Http404("Cannot view this account")

    loop = event_loop()
    cli = Client(net_profile=settings.BLOCKCHAIN_CONNECTION)
    org1_admin = cli.get_user(org_name='Org1', name='Admin')
    account_id = str(account_id)
    args = [account_id]
    new_gateway = Gateway()  # Creates a new gateway instance
    options = {'wallet': ''}
    loop.run_until_complete(new_gateway.connect(settings.BLOCKCHAIN_CONNECTION, options))
    new_network = loop.run_until_complete(new_gateway.get_network('mychannel', org1_admin))
    cli = new_gateway.client
    new_contract = new_network.get_contract('bankcode')
    response = cli.chaincode_query(requestor=org1_admin,
                                   channel_name=new_contract.network.channel.name,
                                   peers=cli._peers,  # pylint: disable=protected-access
                                   args=args,
                                   cc_name=new_contract.cc_name,
                                   fcn='getBankStatement')
    result = loop.run_until_complete(response)

    return TemplateResponse(request, 'pages/get_bank_statement_blockchain.html', {
        'result': result,
    })


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
        if django_user is not None and not django_user.is_active:
            django_user = None
        if django_user is None:
            form.add_error(None, "Username or password is incorrect")
        else:
            try:
                persimmon_user = User.objects.select_for_update().get(django_user=django_user)
            except User.DoesNotExist:
                form.add_error(None, "Username or password is incorrect")

    # pass 2: check otp
    if form.is_valid():
        # if we get this far and we need to render the form again don't wipe the password and display the otp field
        form.fields['password'].widget.render_value = True
        form.fields['login_code'] = forms.CharField(widget=forms.TextInput(attrs={'class': 'use-otpkeyboard-input'}))
        form.full_clean()

        # if the form is no longer valid no otp was not entered, generate and send it
        if not form.is_valid():
            form.errors.clear()
            form.add_error(None, "Please enter the code we just sent to your phone")

            otp = '%06d' % random.randint(100000, 999999)
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
            SignInHistory.objects.create(user=persimmon_user)
            django_login(request, django_user)
            return TemplateResponse(request, 'pages/login_success.html', {})

    return TemplateResponse(request, 'pages/login.html', {
        'form': form,
    })


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('address',)

    address = forms.CharField(max_length=200, widget=forms.Textarea)


class UserPhoneForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone',)

    phone = forms.CharField(
        label='Phone Number',
        max_length=12,
        validators=[RegexValidator(r'^[0-9]{10}$', 'Enter a 10-digit phone number, e.g. 0123456789.')])


class UserNameForm(forms.ModelForm):
    class Meta:
        model = DjangoUser
        fields = ('first_name', 'last_name')

    first_name = forms.CharField()
    last_name = forms.CharField()


class UserEmailForm(forms.ModelForm):
    class Meta:
        model = DjangoUser
        fields = ('email',)

    email = forms.EmailField()


def edit_user(request, user_id):
    # load the users we're working with - the editor and the to-be-edited
    user_editor = current_user(request)
    try:
        user_edited = User.objects.get(id=user_id, django_user__is_active=True)
    except User.DoesNotExist as exc:
        raise Http404("No such user") from exc
    original_email = user_edited.email
    original_address = user_edited.address
    original_phone = user_edited.phone
    original_firstname = user_edited.django_user.first_name
    original_lastname = user_edited.django_user.last_name

    # check if editing this user is allowed, and furthermore,
    # whether we are allowed to bypass the verification steps.
    # we use editing_self to indicate whether verification is required
    if user_editor == user_edited:
        editing_self = True
    elif user_editor.employee_level >= EmployeeLevel.MANAGER:
        if user_edited.employee_level > EmployeeLevel.CUSTOMER and user_editor.employee_level < EmployeeLevel.ADMIN:
            raise Http404("Cannot edit this user")
        editing_self = False
    else:
        raise Http404("Cannot edit this user")

    # collect the post data into form objects
    form_address = UserAddressForm(request.POST or None, instance=user_edited)
    form_phone = UserPhoneForm(request.POST or None, instance=user_edited)
    form_name = UserNameForm(request.POST or None, instance=user_edited.django_user)
    form_email = UserEmailForm(request.POST or None, instance=user_edited.django_user)

    if form_address.is_valid() and form_address.cleaned_data['address'] != original_address:
        UserEditRequest.objects.create(user=user_edited, address=form_address.cleaned_data['address'])
        form_address.add_error(None, "Address update submitted for approval")
    else:
        form_address = UserAddressForm(instance=user_edited)

    if form_name.is_valid() and (
            form_name.cleaned_data['first_name'] != original_firstname or
            form_name.cleaned_data['last_name'] != original_lastname):
        UserEditRequest.objects.create(user=user_edited,
                                       firstname=form_name.cleaned_data['first_name'],
                                       lastname=form_name.cleaned_data['last_name'])
        form_name.add_error(None, "Name change submitted for approval")
    else:
        form_name = UserNameForm(instance=user_edited.django_user)

    if form_email.is_valid() and form_email.cleaned_data['email'] != original_email:
        if not editing_self:
            form_email.save()
            form_email.add_error(None, "Email address updated")
        else:
            # code 1 says username wants to change to new email, certified by old email
            verification_code_1 = make_verification_code(
                'change_email_1',
                user_edited.username,
                form_email.cleaned_data['email'],
                original_email)
            # code 2 says username wants to change to new email, certified by new email
            verification_code_2 = make_verification_code(
                'change_email_2',
                user_edited.username,
                form_email.cleaned_data['email'],
                form_email.cleaned_data['email'])
            form_email.fields['email_verification_1'] = forms.CharField()
            form_email.fields['email_verification_2'] = forms.CharField()
            form_email.full_clean()
            if not form_email.is_valid():
                mail.send_mail(
                    "Persimmon verification code",
                    f"Here is code 1 to update your email: {verification_code_1}",
                    settings.EMAIL_SENDER,
                    [original_email]
                )
                mail.send_mail(
                    "Persimmon verification code",
                    f"Here is code 2 to update your email: {verification_code_2}",
                    settings.EMAIL_SENDER,
                    [form_email.cleaned_data['email']]
                )
                form_email.errors.clear()
                form_email.add_error(
                    'email_verification_1',
                    'Please check both your emails and enter the codes we sent you here')
            elif form_email.cleaned_data['email_verification_1'] != verification_code_1 or \
                    form_email.cleaned_data['email_verification_2'] != verification_code_2:
                form_email.add_error('email_verification_1', 'Invalid codes')
            else:
                form_email.save()
                form_email.fields.pop('email_verification_1', None)
                form_email.fields.pop('email_verification_2', None)
                form_email.add_error(None, "Email address updated")
    else:
        form_email = UserEmailForm(instance=user_edited.django_user)

    if form_phone.is_valid() and form_phone.cleaned_data['phone'] != original_phone:
        if not editing_self:
            form_phone.save()
            form_phone.add_error(None, "Phone address updated")
        else:
            # code 1 says username wants to change to new phone, certified by old phone
            verification_code_1 = make_verification_code(
                'change_phone_1',
                user_edited.username,
                form_phone.cleaned_data['phone'],
                original_phone)
            # code 2 says username wants to change to new phone, certified by new phone
            verification_code_2 = make_verification_code(
                'change_phone_2',
                user_edited.username,
                form_phone.cleaned_data['phone'],
                form_phone.cleaned_data['phone'])
            form_phone.fields['phone_verification_1'] = forms.CharField()
            form_phone.fields['phone_verification_2'] = forms.CharField()
            form_phone.full_clean()
            if not form_phone.is_valid():
                try:
                    send_sms(
                        f"Here is code 2 to update your phone number: {verification_code_2}",
                        settings.SMS_SENDER,
                        [form_phone.cleaned_data['phone']]
                    )
                except Exception:  # pylint: disable=broad-except
                    form_phone.add_error("phone", "This phone number is not imported into our system. See user guide.")
                else:
                    send_sms(
                        f"Here is code 1 to update your phone number: {verification_code_1}",
                        settings.SMS_SENDER,
                        [original_phone]
                    )
                    form_phone.errors.clear()
                    form_phone.add_error(
                        'phone_verification_1',
                        'Please check both your phones and enter the codes we sent you here')
            elif form_phone.cleaned_data['phone_verification_1'] != verification_code_1 or \
                    form_phone.cleaned_data['phone_verification_2'] != verification_code_2:
                form_phone.add_error('phone_verification_1', 'Invalid codes')
            else:
                form_phone.save()
                form_phone.fields.pop('phone_verification_1', None)
                form_phone.fields.pop('phone_verification_2', None)
                form_phone.add_error(None, "Phone number updated")
    else:
        form_phone = UserPhoneForm(instance=user_edited)

    return TemplateResponse(request, 'pages/edit_user.html', {
        'form_name': form_name,
        'form_email': form_email,
        'form_phone': form_phone,
        'form_address': form_address,
    })


def close_account(request, user_id):
    user = current_user(request, required_auth=EmployeeLevel.MANAGER)
    try:
        closed_user = User.objects.get(id=user_id, django_user__is_active=True)
    except User.DoesNotExist as exc:
        raise Http404("No such user") from exc

    if closed_user.employee_level > EmployeeLevel.CUSTOMER and user.employee_level < EmployeeLevel.ADMIN:
        raise Http404("Cannot modify this account")

    if request.POST:
        closed_user.django_user.is_active = False
        closed_user.django_user.save()
        Transaction.objects.filter(Q(account_add__owner=closed_user)
                                                       | Q(account_subtract__owner=closed_user))\
            .select_for_update().filter(approval_status=ApprovalStatus.PENDING)\
            .update(approval_status=ApprovalStatus.DECLINED)
        return TemplateResponse(request, 'pages/close_account_success.html', {})

    return TemplateResponse(request, 'pages/close_account.html', {
        'view_user': closed_user,
    })


class UserLookupForm(forms.Form):
    search_term = forms.CharField()


def user_lookup(request):
    current_user(request, required_auth=EmployeeLevel.TELLER)
    form = UserLookupForm(request.POST)

    if form.is_valid():
        terms = form.cleaned_data['search_term'].split()
        query = User.objects.select_for_update().filter(django_user__is_active=True)
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
    amount_text = f'{num2words(int(trans.transaction))} dollars and ' \
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
