#:coding=utf-8:

class LazyUser(object):
    """
    Lazily creates the user object.
    """
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_newauth_cached_user'):
            from newauth.api import get_user_from_request
            request._newauth_cached_user = get_user_from_request(request)
        return request._newauth_cached_user

class AuthMiddleware(object):
    """
    Middleware for getting the current user object
    and attaching it to the request.
    """
    def process_request(self, request):
        from django.conf import settings
        from newauth.constants import DEFAULT_USER_PROPERTY

        user_prop = getattr(settings, 'NEWAUTH_USER_PROPERTY', DEFAULT_USER_PROPERTY)
        setattr(request.__class__, user_prop, LazyUser())
        return None
