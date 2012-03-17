=====================================
Limiting access to logged-in users
=====================================

The raw way
-------------------

The simple, raw way to limit access to pages is to check
:func:`request.user.is_authenticated() <newauth.api.UserBase.is_authenticated>`
and either redirect to a login page or display an error message. This is largely
based off of django's `User.is_authenticated() <https://docs.djangoproject.com/en/1.3/topics/auth/#django.contrib.auth.models.User.is_authenticated>`_ method.

.. code-block:: python

    from django.http import HttpResponseRedirect

    def my_view(request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/login/?next=%s' % request.path)
        # ...

The login_required decorator
-----------------------------------

You can limit access to logged-in users using the 
:func:`login_required() <newauth.decorators.login_required>`
decorator.  The login_required decorator can be used in the same way that
the Django login_required decorator can be used but with some notable differences.

:func:`login_required() <newauth.decorators.login_required>`
can take no arguments in the same way that the
`login_required() <https://docs.djangoproject.com/en/1.3/topics/auth/#django.contrib.auth.decorators.login_required>`_ decorator for django auth does.

.. code-block:: python

    from newauth.decorators import login_required

    @login_required
    def my_view(request):
        ...

It also takes the same keyword arguments.

.. code-block:: python

    from newauth.decorators import login_required

    @login_required(login_url="/mylogin", redirect_field_name="next_url")
    def my_view(request):
        ...

However it also can take a list of backend names so that you can specify
the specific backends that are required to execute that view.

.. code-block:: python

    from newauth.decorators import login_required

    @login_required(["default", "backend2"])
    def my_view(request):
        ...

We'll tie everything we have set up so far in :doc:`the
next section <settings>` by adding the settings to make a
working example.
