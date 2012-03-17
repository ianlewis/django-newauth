#:coding=utf-8:

from django import forms
from django.db import transaction
from django.conf import settings
from django.contrib import admin
from django.http import Http404
from django.shortcuts import redirect
from django.utils.html import escape
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.admin.helpers import AdminForm
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.decorators import method_decorator
from django.template import RequestContext

csrf_protect_m = method_decorator(csrf_protect)

class UserBaseAdmin(admin.ModelAdmin):
    list_display = ('get_display_name',)
    search_fields = ('pk',)

class BasicUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^[\w.@+-]+$',
        help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    def __init__(self, *args, **kwargs):
        super(BasicUserCreationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            self._meta.model.objects.get(username=username)
        except self._meta.model.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(BasicUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class PasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()
        return self.user


class BasicUserAdmin(UserBaseAdmin):
    add_form_template = 'admin/newauth/basicuser/add_form.html'
    change_user_password_template = None
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    add_form = BasicUserCreationForm
    change_password_form = PasswordChangeForm
    search_fields = ('pk', 'username')
    ordering = ('username',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(BasicUserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': modelform_factory(self.model, self.add_form),
                'fields': flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(BasicUserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        from django.conf.urls.defaults import patterns
        return patterns('',
            (r'^(.+)/password/$', self.admin_site.admin_view(self.user_change_password))
        ) + super(BasicUserAdmin, self).get_urls()

    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404('Your user does not have the "Change user" permission. In order to add users, Django requires that your user account have both the "Add user" and "Change user" permissions set.')
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': self.model._meta.get_field('username').help_text,
        }
        extra_context.update(defaults)
        return super(BasicUserAdmin, self).add_view(request, form_url, extra_context)

    def user_change_password(self, request, id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.model, pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Password changed successfully.'))
                return redirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': form.base_fields.keys()})]
        adminForm = AdminForm(form, fieldsets, {})

        return render_to_response(self.change_user_password_template or 'admin/newauth/basicuser/change_password.html', {
            'title': _('Change password: %s') % escape(str(user)),
            'adminForm': adminForm,
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))
