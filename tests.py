import os
import sys
import django

BASE_PATH = os.path.dirname(__file__)

def main():
    """
    Standalone django model test with a 'memory-only-django-installation'.
    You can play with a django model without a complete django app installation.
    http://www.djangosnippets.org/snippets/1044/
    """
    sys.exc_clear()

    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings

    global_settings.INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.contenttypes',
        'newauth',
        'newauth.tests.testapp',
    )
    global_settings.DATABASE_ENGINE = "sqlite3"
    global_settings.DATABASE_NAME = ":memory:"
    global_settings.ROOT_URLCONF='newauth.tests.test_urls'
    global_settings.MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'newauth.middleware.AuthMiddleware',
    )
    global_settings.NEWAUTH_BACKENDS = {
        'default': {
            'backend': 'newauth.backend.BasicUserBackend',
            'user': 'newauth.tests.testapp.models.TestBasicUser',
            'anon_user': 'newauth.api.BasicAnonymousUser',
        }
    }

    from django.test.utils import get_runner
    test_runner = get_runner(global_settings)

    if django.VERSION > (1,2):
        test_runner = test_runner()
        failures = test_runner.run_tests(['newauth'])
    else:
        failures = test_runner(['newauth'], verbosity=1)
    sys.exit(failures)

if __name__ == '__main__':
    main()
