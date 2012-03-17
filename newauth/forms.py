#:coding=utf-8:

from django.utils.translation import ugettext_lazy as _
from django import forms

from newauth.api import authenticate

__all__ = (
    'BaseAuthForm',
    'BasicAuthForm',
)

class BaseAuthForm(forms.Form):
    """
    A base authentication form. Authentication forms
    can subclass this form and implement the
    get_credentials() method which will return a
    dictionary of credentials from self.cleaned_data
    that can be used with authenticate()
    """
    default_error_messages = {
        'auth_failure': _("Please enter a correct credentials."),
    }

    def __init__(self, *args, **kwargs):
        super(BaseAuthForm, self).__init__(*args, **kwargs)
        self.user_cache = None

    def get_credentials(self):
        """
        Gets credentials as a dict object from self.cleaned_data
        """
        raise NotImplemented

    def clean(self):
        credentials = self.get_credentials()
        if credentials:
            self.user_cache = authenticate(**credentials)
            if self.user_cache is None:
                raise forms.ValidationError(self.default_error_messages['auth_failure'])
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.pk
        return None

    def get_user(self):
        """
        Gets the cached user object for the user that logged in using
        this form.
        """
        return self.user_cache

class BasicAuthForm(BaseAuthForm):
    """
    A basic authentication form that will authenticate
    a user using a username and password. Useful for
    subclasses of BasicUser.
    """
    default_error_messages = {
        'auth_failure': _("Please enter a correct username and password. Note that both fields are case-sensitive."),
    }

    username = forms.CharField(label=_("Username"), max_length=30)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def get_credentials(self):
        return {
            'username': self.cleaned_data.get('username'),
            'password': self.cleaned_data.get('password'),
        }
