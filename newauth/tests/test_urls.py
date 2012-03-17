#':coding=utf-8:

from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    (r'^testapp/', include('newauth.tests.testapp.urls')),
    (r'^account/', include('newauth.urls'))
)
