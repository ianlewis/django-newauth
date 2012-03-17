#:coding=utf-8:

import re

from django.template import RequestContext
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect, render_to_response
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.conf import settings

from newauth.api import login as auth_login, logout as auth_logout
from newauth.forms import BasicAuthForm

@csrf_protect
@never_cache
def login(request, next_page=None,
          template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=BasicAuthForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    
    if request.method == "POST":
        form = authentication_form(data=request.POST)

        if form.is_valid():
            if hasattr(request, 'session') and not request.session.test_cookie_worked():
                from django.forms.forms import NON_FIELD_ERRORS
                # Add an error to the form causing it to invalidate.
                form._errors[NON_FIELD_ERRORS] = form.error_class([_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in.")])
            else:
                # Light security check -- make sure redirect_to isn't garbage.
                if not redirect_to or ' ' in redirect_to:
                    redirect_to = next_page or settings.LOGIN_REDIRECT_URL
                
                # Heavier security check -- redirects to http://example.com should 
                # not be allowed, but things like /view/?param=http://example.com 
                # should be allowed. This regex checks if there is a '//' *before* a
                # question mark.
                elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = next_page or settings.LOGIN_REDIRECT_URL
               
                # Okay, security checks complete. Log the user in.
                auth_login(request, form.get_user())

                if hasattr(request, 'session') and request.session.test_cookie_worked():
                    request.session.delete_test_cookie()

                return redirect(redirect_to)

    else:
        form = authentication_form()

    if hasattr(request, 'session'):
        request.session.set_test_cookie()
    
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
    }, context_instance=RequestContext(request))

def logout(request, next_page=None, template_name='registration/logged_out.html', redirect_field_name=REDIRECT_FIELD_NAME):
    "Logs out the user and displays 'You are logged out' message."
    auth_logout(request)
    if next_page is None:
        redirect_to = request.REQUEST.get(redirect_field_name, getattr(settings, 'LOGOUT_REDIRECT_URL', ''))
        if redirect_to:
            return redirect(redirect_to)
        else:
            return render_to_response(template_name, {
                'title': _('Logged out')
            }, context_instance=RequestContext(request))
    else:
        # Redirect to this page until the session has been cleared.
        return redirect(next_page or request.path)

def logout_then_login(request, login_url=None):
    "Logs out the user if he is logged in. Then redirects to the log-in page."
    return logout(request, login_url or settings.LOGIN_URL)
