from bootstrap_datepicker_plus import DateTimePickerInput

from django.core import mail
from django.http import Http404
from django.core.validators import RegexValidator
from django import forms, urls
from django.template.response import TemplateResponse
from django.contrib.auth import logout as django_logout, login as django_login, forms as auth_forms
from django.conf import settings
from sms import send_sms

from ..models import BankAccount, ApprovalStatus, DjangoUser, EmployeeLevel, User, Transaction, Appointment
from . import current_user, apis
from ..transaction_approval import check_approvals, applicable_approvals


# index for website/ to check if url views are working
def index(request):
    return TemplateResponse(request, 'pages/home.html', {})


def logout(request):
    current_user(request)
    django_logout(request)
    return TemplateResponse(request, 'pages/logout.html', {})


class ResetPasswordForm(forms.Form):
    email = forms.CharField(max_length=200)


def reset_password_sent(request):
    current_user(request, expect_not_logged_in=True)

    return TemplateResponse(request, 'pages/reset_password_sent.html', {})


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
    user = current_user(request)
    form = ScheduleAppointment(request.POST or None)

    if form.is_valid():
        for teller in User.objects.filter(employee_level=1).exclude(django_user=user.django_user):
            if not Appointment.objects.filter(employee=teller, time=form.cleaned_data['time']):
                newapp = Appointment.objects.create(
                    employee=teller,
                    customer=user,
                    time=form.cleaned_data['time'],
                )
                newapp.save()
                return TemplateResponse(request, 'pages/appointmentbooked.html', {
                    'teller': teller.name,
                    'time': form.cleaned_data['time'],
                })

        form.add_error(None, "No employees available at given time")

    appointments = Appointment.objects.filter(customer=user).all()

    return TemplateResponse(request, 'pages/schedule_appointment.html', {
        'form': form,
        "appointments": appointments,
        "login_user": user
    })


class CreatePersimmonUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('address', 'phone')

    address = forms.CharField(max_length=200, widget=forms.Textarea)
    phone = forms.CharField(
        label='Phone Number',
        max_length=12,
        validators=[RegexValidator(r'^[0-9]{10}$', 'Enter a 10-digit phone number, e.g. 0123456789.')])


class CreateDjangoUserForm(auth_forms.UserCreationForm):
    class Meta:
        model = DjangoUser
        fields = ('first_name', 'last_name', 'email', 'username')

    # these are for some reason autocreated incorrectly wrt the 'required' field. do it manually
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField()

    def clean(self):
        cleaned = super().clean()

        if DjangoUser.objects.filter(username=cleaned.get("username")).exists():
            raise forms.ValidationError("Username is already taken")
        if DjangoUser.objects.filter(email=cleaned.get("email")).exists():
            raise forms.ValidationError("Email is already in use")

        return cleaned


def create_user_page(request):
    current_user(request, expect_not_logged_in=True)

    form1 = CreatePersimmonUserForm(request.POST or None)
    form2 = CreateDjangoUserForm(request.POST or None)
    form2.fields['password1'].widget.render_value = True
    form2.fields['password2'].widget.render_value = True

    if form1.is_valid() and form2.is_valid():
        verification_code_email = apis.make_verification_code(
            'create_account_email',
            form2.cleaned_data['username'],
            form2.cleaned_data['email'])
        verification_code_phone = apis.make_verification_code(
            'create_account_phone',
            form2.cleaned_data['username'],
            form1.cleaned_data['phone'])
        form1.fields['email_verification'] = forms.CharField()
        form1.fields['phone_verification'] = forms.CharField()
        form1.full_clean()

        if form1.has_error("email_verification"):
            mail.send_mail(
                "Persimmon verification code",
                f"Here is the code to verify your email: {verification_code_email}",
                settings.EMAIL_SENDER,
                [form2.cleaned_data['email']],
            )
            form1.errors["email_verification"].clear()
            form1.add_error(
                'email_verification',
                'Please check your email and enter the code we sent you here')
        elif form1.cleaned_data['email_verification'] != verification_code_email:
            form1.add_error('email_verification', 'Invalid code')

        if form1.has_error("phone_verification"):
            send_sms(
                f"Here is the code to verify your phone number: {verification_code_phone}",
                settings.SMS_SENDER,
                [form1.cleaned_data['phone']],
            )
            form1.errors["phone_verification"].clear()
            form1.add_error(
                'phone_verification',
                'Please check your phone and enter the code we sent you here')
        elif form1.cleaned_data['phone_verification'] != verification_code_phone:
            form1.add_error('phone_verification', 'Invalid code')

    if form1.is_valid() and form2.is_valid():
        try:
            django_user = form2.save()
        except Exception as exc:  # pylint: disable=broad-except
            form2.add_error(None, str(exc))
        else:
            form1.instance.django_user = django_user
            form1.instance.employee_level = EmployeeLevel.CUSTOMER
            try:
                form1.save()
            except Exception as exc:  # pylint: disable=broad-except
                django_user.delete()
                form1.add_error(None, str(exc))
            else:
                django_login(request, django_user)
                return TemplateResponse(request, 'pages/create_account_success.html', {})

    return TemplateResponse(request, 'pages/create_account.html', {
        'form1': form1,
        'form2': form2,
    })


def account_overview_page(request, user_id):
    login_user = current_user(request)
    try:
        view_user = User.objects.get(id=user_id)
        if view_user != login_user and login_user.employee_level < EmployeeLevel.TELLER:
            raise User.DoesNotExist
    except User.DoesNotExist as exc:
        raise Http404("This account cannot be viewed") from exc

    accounts = BankAccount.objects.filter(owner=view_user).exclude(approval_status=ApprovalStatus.DECLINED).all()
    return TemplateResponse(request, 'pages/account_overview.html', {
        "view_user": view_user,
        "accounts": accounts,
    })


def statement_page(request, number):
    user = current_user(request, expect_not_logged_in=False)

    try:
        account = BankAccount.objects.get(id=number)
        if user != account.owner and user.employee_level < EmployeeLevel.TELLER:
            raise BankAccount.DoesNotExist
    except BankAccount.DoesNotExist as exc:
        raise Http404("This account cannot be viewed") from exc

    transactions = account.transactions.exclude(approval_status=ApprovalStatus.DECLINED) \
        .order_by('approval_status', '-date')
    statement = []

    for transaction in transactions:

        entry = transaction.for_one_account(account)
        if transaction.approval_status == ApprovalStatus.PENDING and check_approvals(transaction, user):
            entry.can_approve = True
        statement.append(entry)

    return TemplateResponse(request, 'pages/bank_account.html', {
        "account": account,
        "statement": statement,
    })


def employee_page(request):
    user = current_user(request, required_auth=EmployeeLevel.TELLER)
    transactions = applicable_approvals(user)
    accounts = BankAccount.objects.filter(approval_status=ApprovalStatus.PENDING)

    return TemplateResponse(request, 'pages/employee_page.html', {
        "pending_transactions": transactions,
        "pending_accounts": accounts,
    })


class OwnAccountField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.str_with_balance()


class MobileATMForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, min_value=0.01)
    account = OwnAccountField(None)
    transfer_type = forms.ChoiceField(choices=[('CREDIT', "Deposit"), ('DEBIT', "Withdrawal")])
    check_recipient = forms.CharField(widget=forms.Textarea(), required=False)

    def __init__(self, qs_1, is_employee, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if is_employee:
            self.fields['account'] = forms.ModelChoiceField(None)
        self.fields['account'].queryset = qs_1


def mobile_atm_page(request):
    user = current_user(request, expect_not_logged_in=False)
    filter_owner = {'owner': user} if user.employee_level == EmployeeLevel.CUSTOMER else {}
    accounts = BankAccount.objects.filter(approval_status=ApprovalStatus.APPROVED, **filter_owner)
    form = MobileATMForm(accounts, user.employee_level != EmployeeLevel.CUSTOMER, request.POST or None)

    if form.is_valid():
        debit = form.cleaned_data['transfer_type'] == 'DEBIT'
        trans = Transaction.objects.create(
            description="Mobile ATM Debit" if debit else "Mobile ATM Credit",
            account_add=None if debit else form.cleaned_data['account'],
            account_subtract=form.cleaned_data['account'] if debit else None,
            transaction=form.cleaned_data['amount'],
            approval_status=ApprovalStatus.PENDING,
            check_recipient=form.cleaned_data['check_recipient'] or None)

        trans.add_approval(user)
        return TemplateResponse(request, 'pages/mobile_atm_success.html', {})

    return TemplateResponse(request, 'pages/mobile_atm.html', {
        'form': form,
    })


class TransferForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, min_value=0.01)
    account_1 = OwnAccountField(None)
    transfer_type = forms.ChoiceField(choices=[('SEND', "Send To"), ('RECV', "Request From")])
    account_2 = forms.ModelChoiceField(None)

    def __init__(self, qs_1, qs_2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account_1'].queryset = qs_1
        self.fields['account_2'].queryset = qs_2


def transfer_page(request):
    user = current_user(request)
    qs_2 = BankAccount.objects.filter(approval_status=ApprovalStatus.APPROVED)
    if user.employee_level == 0:
        qs_1 = BankAccount.objects.filter(owner=user, approval_status=ApprovalStatus.APPROVED)
    else:
        qs_1 = qs_2
    form = TransferForm(qs_1, qs_2, request.POST or None)
    if form.is_valid():
        send = form.cleaned_data['transfer_type'] == 'SEND'
        sender = form.cleaned_data['account_1'] if send else form.cleaned_data['account_2']
        receiver = form.cleaned_data['account_2'] if send else form.cleaned_data['account_1']
        trans = Transaction.objects.create(
            transaction=form.cleaned_data['amount'],
            account_add=receiver,
            account_subtract=sender,
            description=f'transfer from {sender.account_number} to {receiver.account_number}',
            approval_status=ApprovalStatus.PENDING,
        )

        trans.add_approval(user)
        check_approvals(trans, user)

        return TemplateResponse(request, 'pages/transfer_success.html', {})

    return TemplateResponse(request, 'pages/transfer.html', {
        'form': form,
    })


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(widget= forms.PasswordInput)


def login_page(request):
    current_user(request, expect_not_logged_in=True)

    return TemplateResponse(request, 'pages/login.html', {
        'form': LoginForm(),
        'api': urls.reverse(apis.persimmon_login),
        'success': urls.reverse(otp_page)
    })


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': "use-otpkeyboard-input"}))


def otp_page(request):
    current_user(request, expect_not_logged_in=True)
    form = OTPForm(request.POST or None)

    if form.is_valid():
        username = request.session.get('username', None)
        sent_otp = request.session.get('sent_otp', None)
        if form.cleaned_data['otp'] != sent_otp:
            form.add_error("otp", "Incorrect code")
        else:
            user = User.objects.get(django_user__username=username)
            django_login(request, user.django_user)
            return TemplateResponse(request, 'pages/login_success.html', {})

    return TemplateResponse(request, 'pages/otp.html', {
        'form': form,
    })
