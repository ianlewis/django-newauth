#:coding=utf-8:

from newauth.models import (
    get_user_model, get_anonymous_user_model
)

__all__ = (
    'BaseAuthBackend',
    'ModelAuthBackend',
    'BasicUserBackend',
)

class BaseAuthBackend(object):
    """
    An base authentication backend class. Authentication
    backends should inherit from this class.
    """
    def __init__(self, backend_name):
        self.backend_name = backend_name

    def authenticate(self, **credentials):
        raise NotImplemented("You must implement the authenticate() method!")

    def get_user(self, user_id):
        raise NotImplemented("You must implement the get_user() method!")

class ModelAuthBackend(BaseAuthBackend):
    """
    An abstract authentication backend that loads
    users based on the get_user_model() method.

    Subclasses only need to implement the authenticate()
    method unless they want to override how
    get_user() works.
    """

    @property
    def user_model(self):
        return get_user_model(self.backend_name)

    @property
    def anon_user_model(self):
        return get_anonymous_user_model(self.backend_name)

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None

class BasicUserBackend(ModelAuthBackend):
    """
    A simple backend to authenticate any subclass
    of BasicUserBase.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = self.user_model.objects.get(username=username)
            if user.check_password(password):
                return user
        except self.user_model.DoesNotExist:
            pass
        return None
