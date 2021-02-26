from django.middleware.csrf import CsrfViewMiddleware, _sanitize_token, _compare_masked_tokens

class HalfCsrfViewMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        return None

    @classmethod
    def check_token(cls, request, token):
        token1 = _sanitize_token(token)
        token2 = cls._get_token(None, request)
        return _compare_masked_tokens(token1, token2)

