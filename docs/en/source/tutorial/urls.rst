========================================
Setting up the Login and Logout Views
========================================

In this section we'll set up the provided login and logout views to
allow for logging in using basic username and password authentication.

URL Routing
------------------

You can add the login and logout views to your url configuration by
including the ``newauth.urls`` module.

.. code-block:: python

    urlpatterns = patterns('',
        # ...
        url(r'^account/', include('newauth.urls')),
        # ...
    )

Customizing the login form
--------------------------------

The provided login view can use any form class that extends the
:class:`BaseAuthForm <newauth.forms.BaseAuthForm>` class.
You can specify the form class by passing it in the ``authentication_form``
argument to the :func:`login <newauth.views.login` view.

.. code-block:: python

    urlpatterns = patterns('',
        # ...
        url(r'^login/$', 'newauth.views.login', name='newauth_login', kwargs={
            'authentication_form': MyLoginForm,
        }),
        # ...
    )

In :doc:`the next section <views>` we'll discuss how to limit access to views
to logged-in users.
