from django.http import Http404

from ..models import EmployeeLevel, User


def current_user(request, required_auth=EmployeeLevel.CUSTOMER, expect_not_logged_in=False):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(django_user=request.user)
        except User.DoesNotExist:
            user = None
    else:
        user = None

    if expect_not_logged_in:
        if user is None:
            return None
        raise Http404("API unavailable to current authentication")

    if user is None:
        raise Http404("API unavailable to current authentication")
    if not user.check_level(required_auth):
        raise Http404("API unavailable to current authentication")
    return user
