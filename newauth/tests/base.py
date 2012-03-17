#:coding=utf-8:

import os
import sys

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.db import reset_queries, DEFAULT_DB_ALIAS, connections
from django.core.signals import request_started

from newauth import api as auth_api

AVAILABLE_SETTINGS = (
    'MIDDLEWARE_CLASSES',
    'NEWAUTH_BACKENDS',
    'NEWAUTH_USER_MODELS',
    'NEWAUTH_USER_PROPERTY',
    'NEWAUTH_SESSION_KEY',
    'NEWAUTH_PASSWORD_ALGO',
    'TEMPLATE_DIRS',
)

# Copied from Django 1.3
class _AssertNumQueriesContext(object):
    def __init__(self, test_case, num, connection):
        self.test_case = test_case
        self.num = num
        self.connection = connection

        # For Django 1.2
        if DJANGO_VERSION < (1,3):
            from types import MethodType
            self.connection.use_debug_cursor = settings.DEBUG

            def django_13_cursor(self):
                if (self.use_debug_cursor or
                    (self.use_debug_cursor is None and settings.DEBUG)):
                    cursor = self.make_debug_cursor(self._cursor())
                else:
                    cursor = self._cursor()
                return cursor
            self.connection.cursor = MethodType(django_13_cursor, self.connection, self.connection.__class__)


    def __enter__(self):
        self.old_debug_cursor = self.connection.use_debug_cursor
        self.connection.use_debug_cursor = True
        self.starting_queries = len(self.connection.queries)
        request_started.disconnect(reset_queries)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.use_debug_cursor = self.old_debug_cursor
        request_started.connect(reset_queries)
        if exc_type is not None:
            return

        final_queries = len(self.connection.queries)
        executed = final_queries - self.starting_queries

        self.test_case.assertEqual(
            executed, self.num, "%d queries executed, %d expected" % (
                executed, self.num
            )
        )

class BaseTestCase(object):
    NEWAUTH_BACKENDS = {
        'default': {
            'backend': 'newauth.backend.BasicUserBackend',
            'user': 'newauth.tests.testapp.models.TestBasicUser',
            'anon_user': 'newauth.api.BasicAnonymousUser',
        },
        'testapp': {
            'backend': (
                'newauth.tests.testapp.backends.TestBackend',
                'newauth.tests.testapp.backends.TestBackend3',
            ),
            'user': 'newauth.tests.testapp.models.TestUser',
            'anon_user': 'newauth.api.BasicAnonymousUser',
        },
        'testapp2': {
            'backend': 'newauth.tests.testapp.backends.TestBackend2',
            'user': 'newauth.tests.testapp.models.TestUser',
            'anon_user': 'newauth.api.BasicAnonymousUser',
        },
        'testapp3': {
            'backend': 'newauth.tests.testapp.backends.TestBackend3',
            'user': 'newauth.tests.testapp.models.TestUser3',
            'anon_user': 'newauth.tests.testapp.models.TestAnonymousUser3',
        }
    }

    TEMPLATE_DIRS = (
        os.path.join(os.path.dirname(__file__), 'templates'),
    )

    def setUp(self):
        # Clear the backend cache so it's reloaded in case the
        # settings have changed
        auth_api._auth_backend_cache = {}

        for setting_name in AVAILABLE_SETTINGS:
            setting_value = getattr(self, setting_name, None)
            setattr(self, "_old_"+setting_name, getattr(settings, setting_name, None))
            if setting_value:
                setattr(settings, setting_name, setting_value)

    def tearDown(self):
        for setting_name in AVAILABLE_SETTINGS:
            old_setting_value = getattr(self, "_old_"+setting_name, None)
            if old_setting_value is None:
                if hasattr(settings, setting_name):
                    delattr(settings, setting_name)
            else:
                setattr(settings, setting_name, old_setting_value)

    # Copied from Django 1.3
    def assertNumQueries(self, num, func=None, *args, **kwargs):
        using = kwargs.pop("using", DEFAULT_DB_ALIAS)
        connection = connections[using]

        context = _AssertNumQueriesContext(self, num, connection)
        if func is None:
            return context

        # Basically emulate the `with` statement here.

        context.__enter__()
        try:
            func(*args, **kwargs)
        except:
            context.__exit__(*sys.exc_info())
            raise
        else:
            context.__exit__(*sys.exc_info())
