#:coding=utf-8:

"""
Alex Gaynor will kill me
"""

from django.db import models
from django.utils.encoding import smart_str, StrAndUnicode
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import memoize
from django.utils.translation import ugettext_lazy as _
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.conf import settings

from newauth.constants import (
    DEFAULT_SESSION_KEY,
    DEFAULT_USER_BACKENDS,
    DEFAULT_USER_PROPERTY,
    DEFAULT_PASSWORD_ALGO,
)

__all__ = (
    'UserBase',
    'AnonymousUserBase',
    'BasicUserManager',
    'BasicUserBase',
    'BasicAnonymousUser',

    'load_backends',
    'get_backends',
    'authenticate',
    'login',
    'logout',
    'get_user_from_request',
    'get_user',
)

class UserBase(models.Model):
    """
    Base User class
    
    Primary key can be defined in sub classes. This
    class makes no assumptions about the format of the
    primary key. Only a pk property (the primary key might
    be something other than id) and the methods
    implemented below can be assumed are present.

    This class also makes no assumptions about underlying
    implementations like what fields are on the User object
    or the table name.
    """
    def is_authenticated(self):
        """
        Returns whether a user is authenticated or not.
        The default is for this method to always return
        true for subclasses of UserBase and False
        for subclasses of AnonymousUserBase
        """
        return True

    def is_anonymous(self):
        return False

    def get_display_name(self):
        """
        Name for display. Usually a username or
        something similar. Usually used for
        public pages. This method should return
        a unicode object.
        """
        from django.utils.encoding import force_unicode
        return force_unicode(self.pk)
    get_display_name.short_description = _('display name')

    def get_real_name(self):
        """
        The user's real name or closest approximation.
        Usually used for private pages etc.
        """
        return self.get_display_name()
    get_display_name.short_description = _('name')

    def __unicode__(self):
        return self.get_display_name()

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')

class AnonymousUserBase(StrAndUnicode):
    """
    A simple anonymous user.
    """
    pk = None

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def is_authenticated(self):
        return False 

    def is_anonymous(self):
        return True 

    def get_display_name(self):
        return u'Guest'
    
    def get_real_name(self):
        return self.get_display_name()

    def __unicode__(self):
        return self.get_display_name()

UNUSABLE_PASSWORD = '!' # This will never be a valid hash

# md5, sha1, crypt
PASSWORD_ALGO = getattr(settings, 'NEWAUTH_PASSWORD_ALGO', DEFAULT_PASSWORD_ALGO)

def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return hsh == get_hexdigest(algo, salt, raw_password)

class BasicUserManager(models.Manager):
    """
    A default manager that can be used with models that
    subclass BasicUserBase.
    """
    def create_user(self, username, password=None): 
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

class BasicUserBase(UserBase):
    """
    A basic user that is authenticated with a
    username and password.

    This class can be subclassed when using
    a simple username password auth system.
    """
    username = models.CharField(_('username'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    password = models.CharField(_('password'), max_length=128, help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))

    objects = BasicUserManager()

    def set_password(self, raw_password):
        """
        Sets the password of the user. Alorithm
        """
        if raw_password is None:
            self.set_unusable_password()
        else:
            import random
            algo = PASSWORD_ALGO
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, raw_password)
            self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        return self.password != UNUSABLE_PASSWORD

    def get_display_name(self):
        return self.username
    get_display_name.short_description = _('username')

    class Meta:
        abstract = True

class BasicAnonymousUser(AnonymousUserBase):
    username=''
    password=None
    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    def has_usable_password(self, raw_password):
        raise NotImplementedError

def _get_backend_data():
    from django.conf import settings

    backend_data = getattr(settings, 'NEWAUTH_BACKENDS', DEFAULT_USER_BACKENDS)
    for key, given_data in backend_data.iteritems():
        data = DEFAULT_USER_BACKENDS['default'].copy() 
        if isinstance(given_data['backend'], basestring):
            given_data['backend'] = (given_data['backend'],)
        data.update(given_data)
        backend_data[key] = data
    return backend_data

def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    if isinstance(import_name, unicode):
        import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise

_auth_backend_cache = {}
def load_backends(backend_name):
    """
    Load the auth backend with the given name
    """
    backend_data = _get_backend_data().get(backend_name)
    if not backend_data:
        raise ImproperlyConfigured('The specified backend "%s" does not exist. Is NEWAUTH_BACKENDS a correctly defined dict?' % backend_name)

    backends = []
    for path in backend_data['backend']:
        try:
            cls = import_string(path)
        except (ImportError, AttributeError), e:
            raise ImproperlyConfigured('Error importing authentication backend %s: "%s"' % (path, e))
        except ValueError, e:
            raise ImproperlyConfigured('Error importing authentication backends. Is NEWAUTH_BACKENDS a correctly defined dict?')
        backends.append(cls(backend_name))
    return backends
load_backends = memoize(load_backends, _auth_backend_cache, 1)

def get_backends(backend_names=None):
    """
    Load all auth backends and return them as a (name, backend) two tuple.
    """
    all_backend_names = _get_backend_data().keys()
    if backend_names is None:
        backend_names = all_backend_names
    else:
        backend_names = filter(lambda b: b in backend_names, all_backend_names)

    backends = []
    for backend_name in backend_names:
        backends.append((backend_name, load_backends(backend_name)))
    return backends

# _backend_name has an underscore so it won't conflict with any
# possible credential keyword arguments
def authenticate(_backend_name=None, **credentials):
    """
    Authenticate a user with using the available auth
    backends. If a _backend_name is provided require
    authentication via the backend with that name.

    If the given credentials are valid, return a User object
    as provided by the backend.
    """
    if _backend_name:
        backends = [(_backend_name, load_backends(_backend_name))]
    else:
        backends = get_backends()

    for backend_name, backend_list in backends:
        for backend in backend_list:
            try:
                user = backend.authenticate(**credentials)
            except TypeError:
                # This backend doesn't accept these credentials as arguments. Try the next one.
                continue
            if user is None:
                continue
            user._backend = backend
            user._backend_name = backend_name
            # TODO: login succeeded. log as info.
            # TODO: authenticate signal
            return user
    # TODO: user failed login. log this as a warning
    # login failures could indicate suspicious activity.
    return None

def login(request, user, backend_name=None):
    """
    Log the user in given the request object. This will
    save any data needed to auth the user (user id and backend name)
    using the auth session storage (not necessarily django sessions).
    """
    from django.conf import settings

    if not hasattr(user, '_backend_name') and backend_name is None:
        # User has no backend set. Cannot login.
        raise ValueError("You must retrieve the user object via a backend "
                         "or via the get_user() function or specify"
                         "a backend_name to the login() function.")

    if not hasattr(request, 'session'):
        raise ImproperlyConfigured("You must add "
                                   "django.contrib.sessions.SessionMiddleware "
                                   "to your MIDDLEWARE_CLASSES in order to support login.")

    # TODO: pre login signal

    session_key = getattr(settings, 'NEWAUTH_SESSION_KEY', DEFAULT_SESSION_KEY)
    current_uid = request.session.get(session_key, {}).get('uid')
    if current_uid and user.pk != current_uid:
        # To avoid reusing another user's session, create a new, empty
        # session if the existing session corresponds to a different
        # authenticated user.
        # TODO: log as info
        request.session.flush()
    else:
        # TODO: log as info
        request.session.cycle_key()

    user_data = {
        'uid': user.pk,
        'bn': backend_name or user._backend_name,
    }
    request.session[session_key] = user_data

    user_prop = getattr(settings, '_USER_PROPERTY', DEFAULT_USER_PROPERTY)
    if hasattr(request, user_prop): 
        setattr(request, user_prop, user)

    # TODO: post login signal

def logout(request):
    """
    Logs the user out. This will clear the user's login session data
    from the auth session storage.
    """
    from django.conf import settings
    # TODO: pre logout signal

    user_prop = getattr(settings, 'NEWAUTH_USER_PROPERTY', DEFAULT_USER_PROPERTY)
    if hasattr(request, user_prop):
        from newauth.models import (
            AnonymousUser, get_anonymous_user_model,
        )

        user = getattr(request, user_prop)
        if hasattr(user, '_backend_name'):
            # Set the current request user to the anonymous user
            # given by the backend of the user being logged out.
            setattr(request, user_prop, get_anonymous_user_model(user._backend_name)())
        elif not isinstance(user, AnonymousUserBase):
            # if the user has no backend set and is not already
            # an anonymous user then set the user to the default
            # anonymous user.
            setattr(request, user_prop, AnonymousUser())
    request.session.flush()

    # TODO: post logout signal

def get_user_from_request(request):
    """
    Gets a user from a request. Used by
    the AuthMiddleware.
    """
    from newauth.models import AnonymousUser
    from django.conf import settings

    if not hasattr(request, 'session'):
        return AnonymousUser()

    session_key = getattr(settings, 'NEWAUTH_SESSION_KEY', DEFAULT_SESSION_KEY)
    session_data = request.session.get(session_key, {})
    user_id = session_data.get("uid")
    backend_name = session_data.get('bn')

    try:
        return get_user(user_id, backend_name)
    except ImproperlyConfigured:
        # We don't trust the backend name given by the request here.
        # Even though storage should be secure if the backend configuration
        # changes this could cause errors to occur so we suppress them here.
        # TODO: log this as a warning
        return AnonymousUser()

def get_user(user_id, backend_name=None):
    """
    Get the user from a user_id. If a backend_name
    is given then the backend with that name will
    be used.

    If a backend_name is not given (default) then
    all backends are tried.

:
    This method should be used to get a user
    rather than getting the user directly from
    the database as it associates the correct
    backend with the user.
    """
    # Avoid making DB queries when we know that the user
    # doesn't exist.
    if user_id is not None:
        if backend_name:
            backends = [(backend_name, load_backends(backend_name))]
        else:
            backends = get_backends()

        for name, backend_list in backends:
            for backend in backend_list:
                user = backend.get_user(user_id=user_id)
                if user:
                    user._backend = backend
                    user._backend_name = name
                    return user

    # If the backend name is given then use
    # that backend's anonymous user
    if backend_name:
        from newauth.models import get_anonymous_user_model
        return get_anonymous_user_model(backend_name)()

    # If no backend is specified and no
    # backend can get the user then use
    # the default anonymous user class.
    from newauth.models import AnonymousUser
    return AnonymousUser()


