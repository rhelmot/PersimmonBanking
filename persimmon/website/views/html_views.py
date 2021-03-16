import string
from bootstrap_datepicker_plus import DateTimePickerInput

from django.core import signing, mail
from django.http import Http404, HttpResponseBadRequest
from django.core.validators import RegexValidator
from django import forms, urls
from django.template.response import TemplateResponse
from django.contrib.auth import logout as django_logout, login as django_login
from django.urls import reverse
from django.views.decorators.http import require_GET

from ..models import BankAccount, ApprovalStatus, DjangoUser, EmployeeLevel, User
from ..common import make_user
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


def reset_password_page(request):
    current_user(request, expect_not_logged_in=True)
    return TemplateResponse(request, 'pages/reset_password.html', {
        'form': ResetPasswordForm(),
        'api': urls.reverse(apis.reset_password),
        'success': urls.reverse(reset_password_sent)
    })


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
    return TemplateResponse(request, 'pages/schedule_appointment.html', {
        'form': ScheduleAppointment(),
        'api': urls.reverse(apis.schedule),
        'success': urls.reverse(schedule_success)
    })


def schedule_success(request):
    current_user(request, expect_not_logged_in=False)
    return TemplateResponse(request, 'pages/appointmentbooked.html', {})


class CreateUserForm(forms.Form):
    first_name = forms.CharField(label='First name',
                                 error_messages={'required': 'Please enter your First name'},
                                 max_length=30, required=True)
    last_name = forms.CharField(label='Last Name',
                                error_messages={'required': 'Please enter your Last name'},
                                max_length=30, required=True)
    email = forms.EmailField()
    username = forms.CharField(label='Username',
                               error_messages={'required': 'Please enter a Username'},
                               max_length=30, required=True)
    phone = forms.CharField(label='Phone Number', max_length=12,
                            error_messages={'incomplete': 'Enter a phone number.'},
                            validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')]
                            , required=True)
    address = forms.CharField(label='address', max_length=50, required=True)
    password = forms.CharField(label='Password', max_length=50, required=True, widget=forms.PasswordInput())
    confirm_password = forms.CharField(
        label='Confirm Password',
        max_length=50,
        required=True,
        widget=forms.PasswordInput())

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password")
        password2 = cleaned.get("confirm_password")

        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match!")

        if DjangoUser.objects.filter(username=cleaned.get("username")).exists():
            raise forms.ValidationError("Username is already taken")
        if DjangoUser.objects.filter(email=cleaned.get("email")).exists():
            raise forms.ValidationError("Email is already in use")

        password = cleaned.get("password")
        special = '!@#$%^&*()<>?'

        if len(password) < 8:
            raise forms.ValidationError("Password not long enough")
        if not any(letter in password for letter in string.ascii_uppercase):
            raise forms.ValidationError("Password does not contain a capital letter")
        if not any(letter in password for letter in string.digits):
            raise forms.ValidationError("Password does not contain a number")
        if not any(letter in password for letter in special):
            raise forms.ValidationError("Password does not contain a special character: one of " + special)


def create_user_page(request):
    current_user(request, expect_not_logged_in=True)

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = make_user(username=form.cleaned_data['username'],
                                 first_name=form.cleaned_data['first_name'],
                                 last_name=form.cleaned_data['last_name'],
                                 password=form.cleaned_data['password'],
                                 email=form.cleaned_data['email'],
                                 phone=form.cleaned_data['phone'],
                                 address=form.cleaned_data['address'])
            new_user.save()

            try:
                encoded_signed = bytes.hex(signing.Signer().sign(new_user.email).encode())
                mail.send_mail(
                    "Persimmon Account Verification",
                    f'Please visit the following link to verify your account: '
                    f'{request.build_absolute_uri(reverse(verify_email) + "?email=" + encoded_signed)}',
                    'noreply@persimmon.rhelmot.io',
                    [new_user.email])
            except Exception:  # pylint: disable=broad-except
                new_user.delete()
                new_user.django_user.delete()  # is this legal
                form.add_error("email", "Could not send email")
            else:
                return TemplateResponse(request, 'pages/create_account_success.html', {
                    "email": new_user.email,
                })

    else:
        form = CreateUserForm()

    return TemplateResponse(request, 'pages/create_account.html', {
        'form': form,
    })


@require_GET
def verify_email(request):
    try:
        email = signing.Signer().unsign(bytes.fromhex(request.GET["email"]).decode())
        account = User.objects.get(django_user__email=email)
    except (ValueError, KeyError, signing.BadSignature, User.DoesNotExist):
        return HttpResponseBadRequest("No. Absolutely not.")

    account.email_verified = True
    account.save()
    django_login(request, account.django_user)

    return TemplateResponse(request, 'pages/email_verified.html', {})


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

    transactions = account.transactions.exclude(approval_status=ApprovalStatus.DECLINED)\
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


def show_info_page(request):
    current_user(request, expect_not_logged_in=False)
    myinfo = apis.get_my_info(request)
    print(myinfo)
    mydic = {'info': myinfo}
    return TemplateResponse(request,'pages/show_info.html', mydic)


def edit_email_success(request):
    return TemplateResponse(request, 'pages/edit_email_success.html', {})


class EditEmail(forms.Form):
    new_email = forms.EmailField()


def edit_email_page(request):
    current_user(request, expect_not_logged_in=False)
    return TemplateResponse(request, 'pages/edit_email.html', {
        'form': EditEmail(),
        'api': urls.reverse(apis.change_my_email),
        'success': urls.reverse(edit_email_success)
    })


def edit_address_success(request):
    return TemplateResponse(request, 'pages/edit_email_success.html', {})


class EditAddress(forms.Form):
    new_address = forms.CharField(label="New Address")


def edit_address_page(request):
    current_user(request, expect_not_logged_in=False)
    return TemplateResponse(request, 'pages/edit_address.html', {
        'form': EditAddress(),
        'api': urls.reverse(apis.change_my_address),
        'success': urls.reverse(edit_address_success)
    })


def edit_phone_success(request):
    return TemplateResponse(request, 'pages/edit_phone_success.html', {})


class EditPhone(forms.Form):
    new_phone = forms.CharField(label='Phone Number', max_length=12,
                            error_messages={'incomplete': 'Enter a phone number.'},
                            validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')]
                            , required=True)


def edit_phone_page(request):
    current_user(request, expect_not_logged_in=False)
    return TemplateResponse(request, 'pages/edit_phone.html', {
        'form': EditPhone(),
        'api': urls.reverse(apis.change_my_phone),
        'success': urls.reverse(edit_phone_success)
    })

def edit_name_success(request):
    return TemplateResponse(request, 'pages/edit_name_success.html', {})


class EditName(forms.Form):
    new_first = forms.CharField(label='First name',
                                 error_messages={'required': 'Please enter your First name'},
                                 max_length=30, required=True)
    new_last = forms.CharField(label='Last Name',
                                error_messages={'required': 'Please enter your Last name'},
                                max_length=30, required=True)


def edit_name_page(request):
    current_user(request, expect_not_logged_in=False)
    return TemplateResponse(request, 'pages/edit_name.html', {
        'form': EditName(),
        'api': urls.reverse(apis.change_my_name),
        'success': urls.reverse(edit_name_success)
    })

