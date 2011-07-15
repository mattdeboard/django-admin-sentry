import os

from django.conf.urls.defaults import *

from admin_sentry import views

AS_ROOT = os.path.dirname(__file__)
STATIC_ROOT = AS_ROOT + '/static'

urlpatterns = patterns('',
    url(r'^$', views.index, name='admin_sentry'),
    url(r'^_static/(?P<path>.*)$', 'django.views.static.serve', 
     {'document_root':STATIC_ROOT},  name="as-media"),
    url(r'^user/(?P<loguser>.*)$', views.by_user, name='user-view'),
    url(r'^changes/(?P<action>[addition|update|deletion])$', views.by_changetype,
        name='change-view'),

)
