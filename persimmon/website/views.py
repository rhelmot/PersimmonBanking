from django.shortcuts import render  # pylint: disable=unused-import

from django.http import HttpResponse
from website.models import EmployeeLevel, User
from django.http import Http404
#checks if user with username has same employeelevel as level
def Securitycheck(request, myusername, level): 
    try:
        x=User.objects.get(username=myusername)
    except User.DoesNotExist:
            raise Http404("epic fail user does not exist")
    
    if x.check_level(level):
        return HttpResponse("success this user match the required permissions")
    else:
        return HttpResponse("fail this user does not have required permissions")

    
#index for website/ to check if url views are working
def index(self):
        return HttpResponse("Hello world")

