from django.urls import path

from .views import html_views, apis

urlpatterns = [
    path('', html_views.index, name='index'),

    path('api/creditdebitfunds/creditdebit', apis.credit_debit_funds),

    path('api/bankaccount/transfer_funds', apis.transfer_funds),
    path('api/user/myinfo', apis.get_all_info),
    path('api/user/changename', apis.change_my_name),
    path('api/user/changeaddress', apis.change_my_address),
    path('api/user/changephone', apis.change_my_phone),
    path('api/user/changeemail', apis.change_my_email),
    path('api/resetpassword', apis.reset_password),
    path('api/session/login', apis.persimmon_login),
    path('api/session/status', apis.login_status),
    path('api/schedule', apis.schedule),

    path('api/bankaccount/approve', apis.approve_bank_account, name='approve-account'),
    path('api/creditdebitfunds/approve', apis.approve_transaction, name='approve-transaction'),
    path('api/bankaccount/new', apis.create_bank_account, name='create-bank-account'),
    path('user-lookup', apis.user_lookup, name='user-lookup'),

    path('reset-password', html_views.reset_password_page),
    path('reset-password/sent', html_views.reset_password_sent),
    path('create-account', html_views.create_user_page, name='create-account'),
    path('verify-email', html_views.verify_email),
    path('user/<int:user_id>', html_views.account_overview_page, name='user'),
    path('user/<int:user_id>/edit', apis.edit_user, name='edit-user'),
    path('account-statement/<int:number>', html_views.statement_page, name='statement'),
    path('logout', html_views.logout, name="logout"),
    path('appointment', html_views.schedule_appointment_page, name='appointment'),
    path('appointment_success', html_views.schedule_success),
    path('employee-view', html_views.employee_page, name='employee'),
    path('user-info', html_views.show_info_page, name='userinfo'),
    path('edit-email', html_views.edit_email_page, name='editemail'),
    path('edit-email-success', html_views.edit_email_success),
    path('edit-address', html_views.edit_address_page, name='editaddress'),
    path('edit-address-success', html_views.edit_address_success),
    path('edit-phone', html_views.edit_phone_page, name='editphone'),
    path('edit-phone-success', html_views.edit_phone_success),
    path('edit-name', html_views.edit_name_page, name='editname'),
    path('edit-name-success', html_views.edit_name_success),
    path('mobile-atm', html_views.mobile_atm_page, name='mobileatm'),
    path('mobile-atm-handel', apis.mobile_atm_handel, name='mobilehandle')

    ]
