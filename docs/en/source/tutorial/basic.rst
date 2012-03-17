============================================
Basic Username/Password Authentication
============================================

newauth provides a ``basic`` submodule that provides some basic functionality
for creating account applications with user models that use basic
username/password authentication. It is a good example of how to use newauth to
create your own user module.

The :class:`BasicUserBase <newauth.api.BasicUserBase>`
model extends the :class:`UserBase <newauth.api.UserBase>`
model and adds a username and password field and implements password checking.
Here we can create a MyUser model as we did before but with username/password
functonality.

.. code-block:: python

    from django.db import models
    from newauth.api import BasicUserBase

    class MyUser(BasicUserBase):
        email = models.EmailField('Email Address')
        profile = models.TextField('Profile Bio', blank=True, null=True)
        avatar = models.ImageField('Avatar', upload_to='profileimg/', blank=True, null=True)

Now we can use the included :class:`BasicUserBackend <newauth.backend.BasicUserBackend>` and
:class:`BasicAuthForm <newauth.forms.BasicAuthForm` in combination
with the :func:`login() <newauth.views.login>` view to authenticate our user.

Here we'll set up the :class:`BasicUserBackend <newauth.backend.BasicUserBackend>` in settings.py:

.. code-block:: python

    NEWAUTH_BACKENDS = {
        'default': {
            'backend': 'newauth.backends.BasicUserBackend',
            'user': 'account.models.MyUser',
            'anon_user': 'account.models.MyAnonymousUser',
        }
    }

The :func:`login() <newauth.views.login>` view uses the
:class:`BasicAuthForm <newauth.forms.BasicAuthForm>`
by default but we can tell it to use the
:class:`BasicAuthForm <newauth.forms.BasicAuthForm>` explicitly.

.. code-block:: python

    from django.conf.urls.defaults import *
    from django.conf import settings

    from newauth.forms import BasicAuthForm

    urlpatterns = patterns('newauth.views',
        url(r'^login$', 'login', name='newauth_login', kwargs={
            'authentication_form': BasicAuthForm,
        }),
    )

We can also use the provided :class:`BasicUserAdmin <newauth.admin.BasicUserAdmin>`
to add functionality to Django's admin. The :class:`BasicUserAdmin <newauth.admin.BasicUserAdmin>`
class implements creating new users and password change in much the same way as Django's auth application. This
makes it very easy to implement usable admin pages:

.. code-block:: python

    from django.contrib import admin
    from beproud.django.auth.basic.admin import BasicUserAdmin
    
    from account.models import MyUser

    admin.site.register(MyUser, BasicUserAdmin)

In :doc:`the next section <urls>` we'll discuss how to set up the login and
logout urls.
