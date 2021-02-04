from django.http import HttpResponse
from django.http import Http404

from .models import User

#checks if user with username has same employeelevel as level
def security_check(request, myusername, level):
    try:
        x = User.objects.get(username=myusername)
    except User.DoesNotExist:
        raise Http404("epic fail user does not exist")
    
    if x.check_level(level):
        return HttpResponse("success this user match the required permissions")
    else:
        return HttpResponse("fail this user does not have required permissions")

#index for website/ to check if url views are working
def index(request):
    return HttpResponse("Hello world")
