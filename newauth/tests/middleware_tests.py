#:coding=utf-8:

from django.test import TestCase as DjangoTestCase

from django import http
from django.contrib.sessions.middleware import SessionMiddleware

from newauth.constants import DEFAULT_USER_PROPERTY
from newauth.middleware import AuthMiddleware

class MiddlewareTest(DjangoTestCase):
    fixtures = ['authutils_testdata.json']

    def setUp(self):
        self.middleware = AuthMiddleware()
        self.session_middleware = SessionMiddleware()

    def test_process_request(self):
        request = http.HttpRequest()
        self.session_middleware.process_request(request)

        request.session['_newauth_user'] = {'uid': 1, 'bn': 'testapp2'}
        self.middleware.process_request(request)

        self.assertTrue(getattr(request, DEFAULT_USER_PROPERTY, None).is_authenticated(),
                "Auth user not authenticated")
