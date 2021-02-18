from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seccheck/<str:myusername>/<int:level>/', views.security_check, name='security_check'),

    path('api/bankaccount/new', views.create_bank_account),
    path('api/bankaccount/get-pending', views.get_pending_bank_accounts),
    path('api/bankaccount/approve', views.approve_bank_account),
    path('api/bankaccount/get', views.get_my_accounts),
    path('api/createuseraccount/create', views.create_user_account),
    path('api/bankaccount/transfer_funds', views.transfer_funds),
    path('api/user/myinfo', views.get_all_info),
    path('api/user/changeaddress', views.change_my_address),
    path('api/user/changephone', views.change_my_phone),
    path('api/user/changeemail', views.change_my_email),
    path('api/session/login', views.persimmon_login),
    path('api/session/logout', views.persimmon_logout),
    path('api/session/status', views.login_status),
]
