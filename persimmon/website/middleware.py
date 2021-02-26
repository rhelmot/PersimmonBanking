import json
from decimal import Decimal
from datetime import datetime
import pydantic

from django.middleware.csrf import CsrfViewMiddleware, _sanitize_token, _compare_masked_tokens
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse, JsonResponse


MAX_REQUEST_LENGTH = 4096


class HalfCsrfViewMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if not getattr(callback, 'api_wrapped', False) and request.method == "POST":
            return self._reject(request, "Cannot POST to non-api methods")
        return None

    @classmethod
    def check_token(cls, request, token):
        token1 = _sanitize_token(token)
        token2 = cls._get_token(None, request)
        return _compare_masked_tokens(token1, token2)


def api_function(func):
    """
    This is a magic function which will automatically deserialize POST request data from JSON and serialize the response
    back to JSON. Additionally, it will typecheck the JSON object structure against the function's type annotations.
    Use it by @annotating your view functions with it.
    """
    gen_namespace = {name: NotImplemented for name in func.__annotations__}
    gen_namespace['__annotations__'] = func.__annotations__
    gen_namespace['Config'] = ApiGenConfig
    request_type = type(func.__name__ + '_args', (pydantic.BaseModel,), gen_namespace)

    def inner(request: HttpRequest, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseBadRequest("Must be a POST request")

        request_data = request.read(MAX_REQUEST_LENGTH + 1)
        if len(request_data) == MAX_REQUEST_LENGTH + 1:
            return HttpResponseBadRequest("Request too large")
        if len(request_data) == 0:
            request_data = b''

        try:
            request_data_dict = json.loads(request_data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponseBadRequest("Data encoding error")

        token = request_data_dict.pop('csrfmiddlewaretoken', None)
        if token is None:
            return HttpResponseForbidden("No CSRF token provided")
        if not HalfCsrfViewMiddleware.check_token(request, token):
            return HttpResponseForbidden("CSRF protection triggered")

        if not isinstance(request_data_dict, dict):
            # force an error in the next stanza
            request_data_dict = {'_': None}

        try:
            request_data_validated = request_type(**request_data_dict)
        except pydantic.ValidationError:
            return HttpResponseBadRequest("Data form error: expecting " + str(func.__annotations__))

        kwargs.update(request_data_validated.dict())
        result = func(request, *args, **kwargs)
        if result is None:
            result = {}
        if isinstance(result, HttpResponse):
            return result
        return JsonResponse(result, safe=False, json_dumps_params=dict(default=encode_extra))

    inner.api_wrapped = True
    return inner


class ApiGenConfig:
    extra = pydantic.Extra.forbid
    validate_all = True


def encode_extra(thing):
    if isinstance(thing, Decimal):
        return str(thing)
    if isinstance(thing, datetime):
        return thing.isoformat()

    raise TypeError(f"Object of type {thing.__class__.__name__} is not serializable")
