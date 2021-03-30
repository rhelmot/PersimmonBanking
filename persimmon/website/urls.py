from django.urls import path

from django.contrib.auth import views as auth_views
from django.views.defaults import page_not_found
from django.http import Http404

from . import views
from .views import html_views, apis

urlpatterns = [
    path('', html_views.index, name='index'),

    path('password_reset',
         auth_views.PasswordResetView.as_view(template_name="pages/reset_password.html"),
         name="password_reset"),
    path('password_reset/sent',
         auth_views.PasswordResetDoneView.as_view(template_name="pages/reset_password_sent.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="pages/reset_password_confirm.html"),
         name="password_reset_confirm"),
    path('reset_password/success',
         auth_views.PasswordResetCompleteView.as_view(template_name="pages/reset_password_success.html"),
         name="password_reset_complete"),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(template_name="pages/password_change.html"),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name="pages/password_change_done.html"),
         name='password_change_done'),

    path('user/new', html_views.create_user_page, name='create-account'),
    path('user/<int:user_id>', html_views.account_overview_page, name='user'),
    path('user/<int:user_id>/edit', apis.edit_user, name='edit-user'),
    path('user/search', apis.user_lookup, name='user-lookup'),

    path('account/new', apis.create_bank_account, name='create-bank-account'),
    path('account/<int:number>', html_views.statement_page, name='statement'),
    path('account/approve', apis.approve_bank_account, name='approve-account'),
    path('account/blockchain', apis.get_bank_statement_from_blockchain,name='get-blockchain'),
    path('account/<int:account_id>/blockchain', apis.get_bank_statement_from_blockchain,name='get-blockchain'),

    path('transaction/<int:tid>/check.png', apis.check_image, name='check'),
    path('transaction/<int:tid>/approve', apis.approve_transaction_page, name='approve-transaction-page'),

    path('appointment', html_views.schedule_appointment_page, name='appointment'),
    path('employee-view', html_views.employee_page, name='employee'),
    path('mobile-atm', html_views.mobile_atm_page, name='mobileatm'),
    path('transfer', html_views.transfer_page, name='transfer'),

    path('login', apis.persimmon_login, name='login'),
    path('otp', html_views.otp_page, name='otp'),
    path('logout', html_views.logout, name="logout"),

    # disable the django admin login
    path('admin/login/', page_not_found, kwargs={'exception': Http404()})
]
