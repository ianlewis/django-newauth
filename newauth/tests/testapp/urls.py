#:coding=utf-8:
from django.conf.urls.defaults import patterns
from django.http import HttpResponse

from newauth.decorators import login_required

urlpatterns = patterns('',
    (r'login_required/', login_required(lambda request: HttpResponse("Spam and Eggs"))),
    (r'testapp_login_required', login_required(["testapp"])(lambda request: HttpResponse("Spam and Eggs"))),
)
