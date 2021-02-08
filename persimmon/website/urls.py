from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:myusername>/<int:level>/', views.security_check, name='security_check'),
    path('appointment/',views.schedule_appointment(),name='appointment'),
]
