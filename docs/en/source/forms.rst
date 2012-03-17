=========================
Authentication Forms
=========================

newauth provides a :class:`BaseAuthForm
<newauth.forms.BaseAuthForm>` which can be used to
authenticate users. You can simply implement the :meth:`get_credentials()
<newauth.forms.BaseAuthForm.get_credentials>` method on the
form and add the needed fields. You can also override the ``auth_failure`` key
in the ``default_error_messages`` dictionary property to provide your own error
message.

.. code-block:: python

    from django import forms
    from django.utils.translation import ugettext_lazy as _
    from newauth.forms import BaseAuthForm

    class AuthForm(BaseAuthForm):
        email = forms.EmailField()
        password = forms.CharField(widget=forms.PasswordInput)

        default_error_messages = {
            'auth_failure': _("Please enter the correct email and password."),
        }
        
        def get_credentials(self):
            return {
                'email': self.cleaned_data['email'],
                'password': self.cleaned_data['password'],
            }

The authenticated user can be obtained by calling the :meth:`get_user()
<newauth.forms.BaseAuthForm.get_user>` method in views after
calling the ``is_valid()`` method. Here is an example of a **very** simple
example of a login view:

.. code-block:: python

    from django.shortcuts import redirect
    from newauth.api import login

    from account.forms import AuthForm

    def mylogin(request):
        form = AuthForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                user = form.get_user()
                
                # Login the user
                login(request, user)
                return redirect('/')
        else:
            return ("""<html><body>"""
                   """<form action="" method="POST">%s</form"""
                   """</body></html>""") % form

In :doc:`the next section <views>` we'll discuss how to limit access to views
to logged-in users.

.. todo:: 

    Move forms doc outside of the tutorial. The tutorial should only include info on basic setup
    and shouldn't contain info on customization etc. It should provide the user with a working example
    at the end of the tutorial.
