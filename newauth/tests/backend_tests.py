#:coding=utf-8:

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase as DjangoTestCase

from newauth.tests.base import BaseTestCase
from newauth.api import load_backends, get_backends

class BackendTestCase(BaseTestCase, DjangoTestCase):
    fixtures = ["authutils_testdata.json"]
    
    def test_load_backend(self):
        from newauth.tests.testapp.backends import TestBackend, TestBackend3

        backends = load_backends("testapp")

        self.assertEqual(len(backends), 2, 'Length of "testapp" backends is not 2')
        self.assertTrue(isinstance(backends[0], TestBackend), '"testapp" backend is not a TestBackend')
        self.assertTrue(isinstance(backends[1], TestBackend3), '"testapp" backend is not a TestBackend3')

    def test_load_notexists_backend(self):
        try:
            load_backends("notexists")
            self.fail("Expected ImproperlyConfigured")
        except ImproperlyConfigured:
            pass

    def test_get_backends(self):
        from newauth.backend import BasicUserBackend
        from newauth.tests.testapp.backends import TestBackend, TestBackend2, TestBackend3

        backends = zip(*get_backends())
        
        self.assertTrue('default' in backends[0])
        self.assertTrue(isinstance(backends[1][list(backends[0]).index('default')][0], BasicUserBackend), 
                '"default" backend is not a BasicUserBackend')

        self.assertTrue('testapp' in backends[0])
        self.assertTrue(isinstance(backends[1][list(backends[0]).index('testapp')][0], TestBackend),
                '"testapp" backend is not a TestBackend')
        self.assertTrue(isinstance(backends[1][list(backends[0]).index('testapp')][1], TestBackend3),
                '"testapp" backend is not a TestBackend3')

        self.assertTrue('testapp2' in backends[0])
        self.assertTrue(isinstance(backends[1][list(backends[0]).index('testapp2')][0], TestBackend2),
                '"testapp2" backend is not a TestBackend2')

        self.assertTrue('testapp3' in backends[0])
        self.assertTrue(isinstance(backends[1][list(backends[0]).index('testapp3')][0], TestBackend3),
                '"testapp3" backend is not a TestBackend3')
