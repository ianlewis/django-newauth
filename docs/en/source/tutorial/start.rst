=================
Getting Started
=================

In this tutorial we will get aquainted with how to use bpauth.
bpauth provides many utilities to use to manage authentication
and user data. Reading the source can be a bit daunting so we'll
go through the most basic usage here.

First we will start by creating a Django application named "account".

::

    $ python manage.py startapp account

Within the account application we will create the user model for
our site. On this model we can add whatever fields might be useful
to our application. The User class will extend from bpauth's
:class:`UserBase <newauth.api.UserBase>` base model class.

Lets edit the models.py:

.. code-block:: python

    from django.db import models
    from newauth.api import UserBase

    class MyUser(UserBase):
        email = models.EmailField('Email Address')
        profile = models.TextField('Profile Bio', blank=True, null=True)
        avatar = models.ImageField('Avatar', upload_to='profileimg/', blank=True, null=True)

Here we have a basic user class for our application. All of the
fields we want can be attached directly on the user object. Next we'll want to
make an anonymous user class that has the same fields as our user class:

.. code-block:: python

    from django.db import models
    from newauth.api import AnonymousUserBase

    class MyAnonymousUser(AnonymousUserBase):
        email = None
        profile = None
        avatar = None

Now let's write a simple view.

.. code-block:: python

    from django.views.generic.simple import direct_to_template

    from account.models import User 

    def my_profile(request):
        return direct_to_template(request, 'account/my_profile.html', {
            'avatar': request.auth_user.avatar,
            'profile': request.auth_user.profile,
        })

You see here we can access all of the fields pertaining to the user's
profile directly on the user object. This is very convenient as you
do not have to use 'get_profile()' to get access to added fields 
for your user as you have to do with Django's contrib.auth application.

The UserBase model defines a number of methods on it to allow third
party applications to interact with your model. Because third party
applications cannot assume you have any fields on your model besides
the 'pk' field, third party applications need to interact with your
MyUser model via these overridable methods.

Here we override the :meth:`get_display_name() <newauth.api.UserBase.get_display_name>`
method to use the first part of the user's email address as their display name.
By default the :class:`UserBase <newauth.api.UserBase>` class simply returns the user's
primary key.

.. code-block:: python

    class MyUser(UserBase):

        # ...

        def get_display_name(self):
            return self.email.split('@')[0]


The :class:`UserBase <newauth.api.UserBase>` class also defines a
:meth:`get_real_name() <newauth.api.UserBase.get_real_name>`
method that can be used for internal, editing, and administrative
functions where a real name would be more appropriate, such
as invoicing etc.

In :doc:`the next section <basic>` we'll discuss how to use newauth to
create user models that use simple username/password authentication.
