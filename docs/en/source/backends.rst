============================
Writing Auth Backends
============================

newauth provides a couple base classes for defining backends. All backends
should extend the BaseAuthBackend. Backend classes are created in much the same
way as you would for the django.contrib.auth app. You need to create an
:meth:`authenticate()
<newauth.backend.BaseAuthBackend.authenticate>` method that
takes the arguments (credentials) that your backend requires and a
:meth:`get_user() <newauth.backend.BaseAuthBackend.get_user>`
method that takes an id and returns an instance of the user.

Here is a very simple backend that authenticates a user using only their
user id. Not a very secure authentication but it illustrates how to write
an authentication backend:

.. code-block:: python

    from nweauth.backend import BaseAuthBackend
    from newauth.models import User

    class UserIdBackend(BaseAuthBackend):
        def authenticate(self, user_id):
            return self.get_user(user_id)

        def get_user(self, user_id):
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist, e:
                return None

Using Model Authentication
-------------------------------

Most of the time, however, you will be creating models extending the
:class:`UserBase <newauth.api.UserBase>` class so you can
extend the provided :class:`ModelAuthBackend
<newauth.backend.ModelAuthBackend>` which provides a default
implementation of :meth:`get_user()
<newauth.backend.ModelAuthBackend.get_user>` which retrieves an
instance of the model associated with the backend in the :attr:`NEWAUTH_BACKENDS
<settings.NEWAUTH_BACKENDS>` in your settings.py.

.. todo:: Code sample

Extending Username/Password Authentication
----------------------------------------------

.. todo:: write me
