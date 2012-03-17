============================
Tieing it all together 
============================

Now we'll tie it all together by setting the appropriate settings in our settings.py.

As we mentioned in the :doc:`Installation <../install>` you'll need to add
``newauth`` to your `INSTALLED_APPS`_:

.. code-block:: python 

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        #...
        'newauth',
        #...
    )

and add the :class:`AuthMiddleware <newauth.middleware.AuthMiddleware>` to your `MIDDLEWARE_CLASSES`_

.. code-block:: python 

    MIDDLEWARE_CLASSES = (
        #...
        'newauth.middleware.AuthMiddleware',
        #...
    )

Here we will set up the :attr:`NEWAUTH_BACKENDS <settings.NEWAUTH_BACKENDS>`
so that we can authenticate and use our MyUser class that we set up earlier.

.. code-block:: python

    NEWAUTH_BACKENDS = {
        'default': {
            'backend': (
                'newauth.backend.BasicUserBackend',
            ),
            'user': 'account.models.MyUser',
            'anon_user': 'account.models.MyAnonymousUser',
        }
    }

And that's it! You should have a simple working example of how to use newauth. newauth
allows a lot of customization so you can continue on and read some of the more
advanced documentation or play some more with the example.

Good Luck!

.. _`INSTALLED_APPS`: http://docs.djangoproject.com/en/1.3/ref/settings/#installed-apps
.. _`MIDDLEWARE_CLASSES`: http://docs.djangoproject.com/en/1.3/ref/settings/#middleware-classes
