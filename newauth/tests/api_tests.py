#:coding=utf-8:

from django.http import HttpRequest
from django.test import TestCase as DjangoTestCase
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware

from newauth.api import authenticate, get_user, login, logout, BasicAnonymousUser
from newauth.middleware import AuthMiddleware
from newauth.tests.base import BaseTestCase
from newauth.constants import DEFAULT_SESSION_KEY

class AuthTestCase(BaseTestCase, DjangoTestCase):
    fixtures = ['authutils_testdata.json']

    def test_authenticate_success(self):
        user = authenticate(user_id=2)
        self.assertTrue(user)
        self.assertEqual(user.id, 2)

        user = authenticate()
        self.assertTrue(user)
        self.assertEqual(user.id, 1)

    def test_authenticate_failure(self):
        user = authenticate(user_id=3)
        self.assertTrue(user is None)

    def test_authenticate_with_backend_success(self):
        user = authenticate("testapp", user_id=1)
        self.assertTrue(user)
        self.assertEqual(user.id, 1)

        user = authenticate("testapp2")
        self.assertTrue(user)
        self.assertEqual(user.id, 1)

    def test_authenticate_with_backend_failure(self):
        user = authenticate("testapp")
        self.assertTrue(user is None)

        user = authenticate("testapp", user_id=3)
        self.assertTrue(user is None)

        user = authenticate("testapp2", user_id=1)
        self.assertTrue(user is None)

        user = authenticate("testapp2", unknown_kwarg=1)
        self.assertTrue(user is None)

    def test_get_user(self):
        user = get_user(1)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(user.id, 1)
        
        user = get_user(2)
        self.assertTrue(user.is_authenticated())
        self.assertEqual(user.id, 2)

    def test_get_user_failure(self):
        user = get_user(3)
        self.assertTrue(user.is_anonymous(), "%s is not anonymous" % user)

    def test_get_user_with_backend(self):
        from newauth.tests.testapp.models import TestUser
        from newauth.tests.testapp.models import TestUser3

        user = get_user(1, 'testapp2')
        self.assertTrue(user, "Could not get User 1")
        self.assertEqual(user.id, 1)
        self.assertTrue(isinstance(user, TestUser))

        user = get_user(2, 'testapp')
        self.assertTrue(user, "Could not get User 2")
        self.assertEqual(user.id, 2)
        self.assertTrue(isinstance(user, TestUser))

        user = get_user(1, 'testapp3')
        self.assertTrue(user, "Could not get User 1")
        self.assertEqual(user.id, 1)
        self.assertTrue(isinstance(user, TestUser3))

    def test_get_user_with_backend_failure(self):
        from newauth.tests.testapp.models import TestAnonymousUser3

        user = get_user(3, 'testapp')
        self.assertTrue(user.is_anonymous(), "%s is not anonymous" % user)
        self.assertTrue(isinstance(user, BasicAnonymousUser))


        user = get_user(2, 'testapp3')
        self.assertTrue(user.is_anonymous(), "%s is not anonymous" % user)
        self.assertTrue(isinstance(user, TestAnonymousUser3))

    def test_get_user_none_anonymous(self):
        """
        Make user that when None is passed as the user_id
        that the user returned is an anonymous user.
        """
        user = get_user(None, None)
        self.assertTrue(user.is_anonymous(), "%s is not anonymous" % user)

    def test_get_user_none_queries(self):
        """
        Test to make sure that we don't do any unnecessary queries
        when the user_id is None
        """
        self.assertNumQueries(0, get_user, None, None)

class LogoutTestCase(BaseTestCase, DjangoTestCase):
    fixtures = ['authutils_testdata.json']

    def test_logout_when_logged_in(self):
        """
        Test to make sure that logout() works when
        the user is logged in.
        """
        from newauth.tests.testapp.models import TestUser3, TestAnonymousUser3
        
        request = HttpRequest()
        user = authenticate(user_id=1, _backend_name='testapp3')
        self.assertTrue(user.is_authenticated(), "%s is not authenticated" % user)

        SessionMiddleware().process_request(request)
        AuthMiddleware().process_request(request)
        self.assertTrue(hasattr(request, 'auth_user'), 'Request has no auth_user attribute')
        self.assertTrue(request.auth_user.is_anonymous(), 'User "%s" is authenticated' % request.auth_user)

        login(request, user, backend_name='testapp3')
        
        session_key = getattr(settings, 'NEWAUTH_SESSION_KEY', DEFAULT_SESSION_KEY)
        session_data = request.session.get(session_key) or {}
        self.assertEquals(session_data.get('uid'), 1)
        self.assertEquals(session_data.get('bn'), 'testapp3')
        self.assertTrue(request.auth_user.is_authenticated(), "%s is not authenticated" % request.auth_user)
        self.assertTrue(isinstance(request.auth_user, TestUser3), 'User "%s" is wrong User class "%s"' % (
            request.auth_user,
            request.auth_user.__class__,
        ))
        self.assertTrue(hasattr(request.auth_user, '_backend'), 'User "%s" has no _backend attribute')
        self.assertTrue(hasattr(request.auth_user, '_backend_name'), 'User "%s" has no _backend_name attribute')

        logout(request)

        session_data = request.session.get(session_key) or {}
        self.assertEquals(session_data.get('uid'), None)
        self.assertEquals(session_data.get('bn'), None)
        self.assertTrue(hasattr(request, 'auth_user'), 'Request has no auth_user attribute')
        self.assertTrue(request.auth_user.is_anonymous(), 'User "%s" is authenticated' % request.auth_user)
        self.assertTrue(isinstance(request.auth_user, TestAnonymousUser3), 'User "%s" is wrong AnonymousUser class "%s"' % (
            request.auth_user,
            request.auth_user.__class__,
        ))

    def test_logout_when_logged_out(self):
        """
        Test to make sure that logout() works when
        the user is not logged in.
        """
        request = HttpRequest()

        SessionMiddleware().process_request(request)
        AuthMiddleware().process_request(request)
        self.assertTrue(hasattr(request, 'auth_user'), 'Request has no auth_user attribute')
        self.assertTrue(request.auth_user.is_anonymous(), 'User "%s" is authenticated' % request.auth_user)

        old_anon_user = request.auth_user

        logout(request)

        session_key = getattr(settings, 'NEWAUTH_SESSION_KEY', DEFAULT_SESSION_KEY)
        session_data = request.session.get(session_key) or {}
        self.assertEquals(session_data.get('uid'), None)
        self.assertEquals(session_data.get('bn'), None)
        self.assertTrue(hasattr(request, 'auth_user'), 'Request has no auth_user attribute')
        self.assertTrue(request.auth_user.is_anonymous(), 'User "%s" is authenticated' % request.auth_user)
        self.assertTrue(request.auth_user is old_anon_user, 'Anonymous User object was changed')
        self.assertTrue(isinstance(request.auth_user, BasicAnonymousUser), 'User "%s" is wrong AnonymousUser class "%s"' % (
            request.auth_user,
            request.auth_user.__class__,
        ))
