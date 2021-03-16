from django.http import Http404

from .views import current_user


def auth(request):
    try:
        user = current_user(request)
    except Http404:
        user = None

    return {
        "persimmon_user": user
    }
