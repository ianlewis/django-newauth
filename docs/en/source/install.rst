===================================
Installation
===================================

Application Install
-----------------------------

Setting up django-newauth is easy.

First install newauth using pip (doesn't work yet)::

    $ pip install django-newauth

Next, add ``newauth`` to `INSTALLED_APPS`_ in your
``settings.py``.

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

Middleware Setup
-----------------------------

You need to install the authentication middleware to support
authentication. Add ``newauth.middleware.AuthMiddleware``
to the `MIDDLEWARE_CLASSES`_ setting in your ``settings.py``.

.. code-block:: python 

    MIDDLEWARE_CLASSES = (
        #...
        'newauth.middleware.AuthMiddleware',
        #...
    )

From here you should proceed to the :doc:`Tutorial <tutorial/start>`.

.. _`INSTALLED_APPS`: http://docs.djangoproject.com/en/1.3/ref/settings/#installed-apps
.. _`MIDDLEWARE_CLASSES`: http://docs.djangoproject.com/en/1.3/ref/settings/#middleware-classes
