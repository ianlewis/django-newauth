class AuthTestCaseMixin(object):
    """
    from django.test import TestCase

    class MyTestCase(TestCase, AuthTestCaseMixin):
        def test_xxx(self):
            self.auth_login(username='spam', password='egg')
            # write some tests
    """

    def auth_login(self, **credentials):
        """
        Sets the Client to appear as if it has successfully logged into a site.

        Returns True if login is possible; False if the provided credentials
        are incorrect, or the user is inactive, or if the sessions framework is
        not available.
        """
        from django.http import HttpRequest
        from django.conf import settings
        from django.utils.importlib import import_module
        from django.contrib.sessions.middleware import SessionMiddleware
        from newauth.middleware import AuthMiddleware
        from newauth.api import authenticate, login
        user = authenticate(**credentials)
        if user and 'django.contrib.sessions' in settings.INSTALLED_APPS:
            engine = import_module(settings.SESSION_ENGINE)

            # Create a fake request to store login details.
            request = HttpRequest()
            SessionMiddleware().process_request(request)
            AuthMiddleware().process_request(request)
            if self.client.session:
                request.session = self.client.session
            else:
                request.session = engine.SessionStore()
            login(request, user)

            # Save the session values.
            request.session.save()

            # Set the cookie to represent the session.
            session_cookie = settings.SESSION_COOKIE_NAME
            self.client.cookies[session_cookie] = request.session.session_key
            cookie_data = {
                'max-age': None,
                'path': '/',
                'domain': settings.SESSION_COOKIE_DOMAIN,
                'secure': settings.SESSION_COOKIE_SECURE or None,
                'expires': None,
            }
            self.client.cookies[session_cookie].update(cookie_data)

            return True
        return False

