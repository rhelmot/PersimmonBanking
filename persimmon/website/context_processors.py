from django.http import Http404


def auth(request):
    from .views import current_user
    try:
        user = current_user(request)
    except Http404:
        user = None

    return {
        "user": user
    }
