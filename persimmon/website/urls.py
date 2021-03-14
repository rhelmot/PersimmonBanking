from django.urls import path

from .views import html_views, apis

urlpatterns = [
    path('', html_views.index, name='index'),

    path('api/bankaccount/new', apis.create_bank_account),
    path('api/bankaccount/get-pending', apis.get_pending_bank_accounts),
    path('api/bankaccount/approve', apis.approve_bank_account),
    path('api/bankaccount/get-statement', apis.bank_statement),

    path('api/creditdebitfunds/creditdebit', apis.credit_debit_funds),
    path('api/creditdebitfunds/approve', apis.approve_transaction),
    path('api/creditdebitfunds/get-pending', apis.get_pending_transactions),

    path('api/createuseraccount/create', apis.create_user_account),
    path('api/bankaccount/transfer_funds', apis.transfer_funds),
    path('api/user/myinfo', apis.get_all_info),
    path('api/user/changeaddress', apis.change_my_address),
    path('api/user/changephone', apis.change_my_phone),
    path('api/user/changeemail', apis.change_my_email),
    path('api/resetpassword', apis.reset_password),
    path('api/session/login', apis.persimmon_login),
    path('api/session/status', apis.login_status),
    path('api/schedule', apis.schedule),

    path('reset-password', html_views.reset_password_page),
    path('reset-password/sent', html_views.reset_password_sent),
    path('create-account', html_views.create_user_page),
    path('create-account-check', html_views.check_create_account),
    path('create-account-success', html_views.create_user_success),
    path('account-overview', html_views.account_overview_page),
    path('account-statement/<int:number>', html_views.temp_statement_page, name='statement'),
    path('logout', html_views.logout, name="logout"),
    path('appointment', html_views.schedule_appointment_page, name='appointment'),
    path('appointment_success', html_views.schedule_success),
]
