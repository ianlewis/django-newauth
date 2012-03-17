#:coding=utf-8:

from django.test import TestCase as DjangoTestCase

from newauth.tests.base import BaseTestCase
from newauth.test import AuthTestCaseMixin

class AuthTestCaseMixinTest(BaseTestCase, AuthTestCaseMixin, DjangoTestCase):
    fixtures = ['authutils_testdata.json']

    def test_auth_login(self):
        self.auth_login(user_id=1)
        self.assertEqual(self.client.session['_newauth_user']['uid'], 1)
