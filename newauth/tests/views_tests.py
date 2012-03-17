#:coding=utf-8:

import urllib

from django.test import TestCase as DjangoTestCase
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

from newauth.tests.base import BaseTestCase
from newauth.tests.testapp.models import TestBasicUser

class ViewsTest(BaseTestCase, DjangoTestCase):
    fixtures = ['authutils_testdata.json']

    def setUp(self):
        super(ViewsTest, self).setUp()
        TestBasicUser.objects.create_user(
            username="testuser",
            password="password",
        )

    def test_login(self):
        # Need to do a get first to for the cookie test.
        self.assertContains(self.client.get('/account/login/'), '<form')
        response = self.client.post('/account/login/', {
            'username': 'testuser',
            'password': 'password',
        })
        self.assertEquals(response.status_code, 302)
        self.assert_(response['Location'].endswith(settings.LOGIN_REDIRECT_URL))

    def test_fail_login(self):
        response = self.client.post('/account/login/', {
            'username': 'testclient',
            'password': 'bad_password', 
        })
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', None, "Please enter a correct username and password. Note that both fields are case-sensitive.")

    def test_fail_login_blank_fields(self):
        # blank username
        response = self.client.post('/account/login/', {
            'username': '',
            'password': 'password', 
        })
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', u'This field is required.')

        # blank password
        response = self.client.post('/account/login/', {
            'username': 'testuser',
            'password': '', 
        })
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, 'form', 'password', u'This field is required.')

    def test_bad_redirect_space(self):
        bad_next_url = 'test space url'
        self.assertContains(self.client.get('/account/login/'), '<form')
        response = self.client.post('/account/login/?%s=%s' % (REDIRECT_FIELD_NAME, urllib.quote(bad_next_url)), {
            'username': 'testuser',
            'password': 'password', 
        })
        self.assertEquals(response.status_code, 302)
        self.assert_(response['Location'].endswith(settings.LOGIN_REDIRECT_URL))

    def test_bad_redirect_empty(self):
        bad_next_url = ''
        self.assertContains(self.client.get('/account/login/'), '<form')
        response = self.client.post('/account/login/?%s=%s' % (REDIRECT_FIELD_NAME, urllib.quote(bad_next_url)), {
            'username': 'testuser',
            'password': 'password', 
        })
        self.assertEquals(response.status_code, 302)
        self.assert_(response['Location'].endswith(settings.LOGIN_REDIRECT_URL))

    def test_bad_redirect_domain(self):
        bad_next_url = 'http://example.com/'
        self.assertContains(self.client.get('/account/login/'), '<form')
        response = self.client.post('/account/login/?%s=%s' % (REDIRECT_FIELD_NAME, urllib.quote(bad_next_url)), {
            'username': 'testuser',
            'password': 'password', 
        })
        self.assertEquals(response.status_code, 302)
        self.assert_(response['Location'].endswith(settings.LOGIN_REDIRECT_URL))

    def test_ok_redirect_domain(self):
        ok_url = '/some/url?param=http://example.com/'
        self.assertContains(self.client.get('/account/login/'), '<form')
        response = self.client.post('/account/login/?%s=%s' % (REDIRECT_FIELD_NAME, urllib.quote(ok_url)), {
        
            'username': 'testuser',
            'password': 'password', 
        })
        self.assertEquals(response.status_code, 302)
        self.assert_(response['Location'].endswith('/some/url?param=http://example.com/'))
