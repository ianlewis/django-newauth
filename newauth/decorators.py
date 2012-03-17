#:coding=utf-8:

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

from django.http import HttpResponseRedirect
from django.utils.decorators import available_attrs
from django.utils.http import urlquote

from newauth.constants import REDIRECT_FIELD_NAME
from newauth.api import get_backends, get_user_from_request

def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(get_user_from_request(request)):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            tup = login_url, redirect_field_name, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator

def login_required(backend_list=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    if callable(backend_list):
        backends = get_backends()
    else:
        backends = get_backends(backend_list)

    backend_names = map(lambda b: b[0], backends)

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and (
            hasattr(u, '_backend_name')) and (
            u._backend_name in backend_names),
        login_url=None,
        redirect_field_name=redirect_field_name
    )

    if callable(backend_list):
        return actual_decorator(backend_list)
    return actual_decorator
