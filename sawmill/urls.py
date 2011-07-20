import os

from django.conf.urls.defaults import *

from admin_sentry import views

AS_ROOT = os.path.dirname(__file__)
STATIC_ROOT = AS_ROOT + '/static'

urlpatterns = patterns('',
    url(r'^$', views.index, name='admin_sentry'),
    url(r'^_static/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root':STATIC_ROOT},  name="as-media"),
    url(r'^login', views.as_login, name='as-login'),
    url(r'^logout', views.as_logout, name='as-logout'),
)
