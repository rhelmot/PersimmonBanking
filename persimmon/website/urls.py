from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seccheck/<str:myusername>/<int:level>/', views.security_check, name='security_check'),

    path('api/bankaccount/new', views.create_bank_account),
    path('api/bankaccount/get-pending', views.get_pending_bank_accounts),
    path('api/bankaccount/approve', views.approve_bank_account),
    path('api/bankaccount/get', views.get_accounts),
    path('api/bankaccount/get-statement', views.bank_statement),

    path('api/creditdebitfunds/creditdebit', views.credit_debit_funds),
    path('api/creditdebitfunds/approve', views.approve_credit_debit_funds),
    path('api/creditdebitfunds/get-pending', views.get_pending_transactions),

    path('api/createuseraccount/create', views.create_user_account),
    path('api/bankaccount/transfer_funds', views.transfer_funds),
    path('api/user/myinfo', views.get_all_info),
    path('api/user/changeaddress', views.change_my_address),
    path('api/user/changephone', views.change_my_phone),
    path('api/user/changeemail', views.change_my_email),
    path('api/resetpassword', views.reset_password),
    path('api/session/login', views.persimmon_login),
    path('api/session/logout', views.persimmon_logout),
    path('api/session/status', views.login_status),
    path('api/appointment', views.schedule_appointment_page, name='appointment'),
    path('api/appointment_success', views.schedule_success),
    path('api/schedule', views.schedule),

    path('reset-password', views.reset_password_page),
    path('reset-password/sent', views.reset_password_sent),
    path('create-account', views.create_user_page),
    path('create-account-check', views.check_create_account),
    path('create-account-success', views.create_user_success),
    path('account-overview', views.account_overview_page),
    path('account-statement/<int:number>', views.temp_statement_page),
    path('logout', views.logout)
]
