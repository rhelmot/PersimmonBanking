from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def schedule_appointment(request):
    return HttpResponse('<h1> Appointment</h1>')
