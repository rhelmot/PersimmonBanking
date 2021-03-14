from bootstrap_datepicker_plus import DateTimePickerInput

from django.http import HttpResponse
from django.core.validators import RegexValidator
from django import forms, urls
from django.template.response import TemplateResponse
from django.contrib.auth import logout as django_logout

from ..models import BankAccount, ApprovalStatus, DjangoUser
from ..common import make_user
from . import current_user, apis


# index for website/ to check if url views are working
def index(request):
    return HttpResponse("Hello world")


def logout(request):
    current_user(request)
    django_logout(request)
    return HttpResponse("you have been logged out")


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


# TODO this should be an API function
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
    user = current_user(request, expect_not_logged_in=False)
    accounts = BankAccount.objects.filter(user=user, approval_status=ApprovalStatus.APPROVED).all()
    return TemplateResponse(request, 'pages/account_overview.html', {
        "user": user,
        "accounts": accounts,
    })


def temp_statement_page(request, number):
    current_user(request, expect_not_logged_in=False)
    statement = "this is where I would show statements for account " +str(number)
    return HttpResponse(statement)
