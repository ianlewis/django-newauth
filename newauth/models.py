#:coding=utf-8:

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import memoize

from newauth.api import _get_backend_data

__all__ = (
    'User',
    'AnonymousUser',
    'get_user_model',
    'get_anonymous_user_model',
)

_user_model_cache = {}
def _get_user_models(model_name=None):
    from newauth.api import import_string

    if model_name is None:
        model_name = 'default'

    backend_data = _get_backend_data()

    try:
        model_path = backend_data[model_name]['user']
        anon_model_path = backend_data[model_name]['anon_user']
    except IndexError:
        if model_name is 'default':
            raise ImproperlyConfigured('A "default" user model is not specified. You must specify a "default" user model. Or maybe NEWAUTH_USER_MODELS isn\'t a correctly defined dict?')
        else:
            raise ImproperlyConfigured('Error importing User model class with name "%s". Is NEWAUTH_USER_MODELS a correctly defined dict?' % model_name)

    try:
        UserCls = import_string(model_path)
    except ImportError:
        raise ImproperlyConfigured('Error importing user model class: "%s"' % model_path)
    except AttributeError:
        raise ImproperlyConfigured('Module does not define a class "%s"' % model_path)

    try:
        AnonUserCls = import_string(anon_model_path)
    except ImportError:
        raise ImproperlyConfigured('Error importing Anonymous user model class: "%s"' % anon_model_path)
    except AttributeError:
        raise ImproperlyConfigured('Module does not define a class "%s"' % anon_model_path)
    return UserCls, AnonUserCls
_get_user_models = memoize(_get_user_models, _user_model_cache, 1)

def get_user_model(model_name=None):
    """
    Used to get access to defined user models.

    from newauth.models import User, get_user_model

    OtherUser = get_user_model('other')

    class MyProfile(models.Model):
        user = models.ForeignKey(User)
        other_user_type = models.ForeignKey(OtherUser)
    """
    return _get_user_models(model_name)[0]

def get_anonymous_user_model(model_name=None):
    return _get_user_models(model_name)[1]

try:
    User = get_user_model('default')
    AnonymousUser = get_anonymous_user_model('default')
except (IndexError, KeyError), e:
    raise ImproperlyConfigured('A "default" user model is not specified. You must specify a "default" user model. Or maybe NEWAUTH_USER_MODELS isn\'t a correctly defined dict?')
