===================================
Overview
===================================

newauth is a kind of authentication framework that allows you to customize user models 
and use the customized user models throughout your application. A number of tools are
provided to allow you to authenticate those customized user objects easily. newauth
has the following features:

Customizable User Models
++++++++++++++++++++++++++++++++++++

The Django auth contrib application has a `User`_ model which contains a number
of fields. New fields cannot be added so you must create a seperate model with
a one to one relationship to the user and retrieve that model object using the
`get_profile()`_ method or via the related field of a OneToOneField
(i.e. user.myprofile).

However, since the User model cannot be modified, you are stuck with all of the
fields present there even if you don't use them. You are also stuck with using
the integer key that comes with a User model. You are out of luck if you would
like to have a User with a UID for a key or have more users than fit into an integer.

Instead of a given User model, newauth provides a :class:`UserBase <newauth.api.UserBase>` abstract model class
which you can extend in your application.  :class:`UserBase <newauth.api.UserBase>` objects don't have any fields
and newauth only depends on the fact that a ``pk`` exists. The id is left to be defined
by the subclass in your own user defined application.

.. Multiple User Models
.. ++++++++++++++++++++++++++++++++
.. 
.. With Django's contrib.auth application you are limited to one type of user model.
.. If you site has multiple types of user which can log in at different places on your site
.. then you are pretty much out of luck.
.. 
.. newauth supports logging in multiple users at once. A website can contain any number
.. of users and any number of logged in users and user types at once, much like
.. multi-account login for Google accounts.

Multiple Auth Backends
+++++++++++++++++++++++++++++++++

newauth supports authentication backends much like Django's contrib.auth application.
However, newauth attaches a name to backends and allows specifying which backend to
use to log the user in. This allows fine grained authentication checking for a specific
type of user.

Auth API and Tools
++++++++++++++++++++++

newauth provides an API much like Django's contrib.auth module which allows you to 
login and logout users programatically. It also provides decorators like the
:func:`login_required() <newauth.decorators.login_required>` decorator.

Storage Backends
++++++++++++++++++++++

newauth allows you to specify how to store information about the logged in user. When
a user logs in it is necessary to store the user's pk and backend in order to get
the user's information on subsequent requests.

Django's contrib.auth application relies on Django sessions to store this information.
However, newauth allows for the use of storage backends other than sessions
such as secure cookies, much like the Django messages framework.

.. _`User`: https://docs.djangoproject.com/en/1.3/topics/auth/#django.contrib.auth.models.User
.. _`get_profile()`: https://docs.djangoproject.com/en/1.3/topics/auth/#django.contrib.auth.models.User.get_profile
