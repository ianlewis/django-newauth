#:coding=utf-8:

DEFAULT_USER_BACKENDS={
    'default': {
        'backend': 'newauth.backend.BasicUserBackend',
        'user': 'newauth.api.BasicUserBase', # TODO: Sane default?
        'anon_user': 'newauth.api.BasicAnonymousUser', # TODO: Sane default?
    }
}

DEFAULT_SESSION_KEY = '_newauth_user'
DEFAULT_USER_PROPERTY='auth_user'
DEFAULT_PASSWORD_ALGO='sha1'
REDIRECT_FIELD_NAME = 'next'

# Base logger name used for logging
LOGGER_NAME='newauth'
