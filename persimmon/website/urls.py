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
    path('api/bankaccount/schedule_appointment', views.schedule_appointment, name='website-appointment').
    path('api/session/login', views.persimmon_login),
    path('api/session/logout', views.persimmon_logout),
    path('api/session/status', views.login_status),
]
