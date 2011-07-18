import sys

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from admin_sentry import settings
from admin_sentry.helpers import *

ACTIONS = {1: 'Addition', 2: 'Change', 3: 'Deletion'}

#@cache_page(300)
@login_required
def index(request):
    filters = []
    #print >> sys.stderr, get_filters()
    for filter_ in get_filters():
        filters.append(filter_(request))

    qs = LogEntry.objects.all().order_by('-action_time')
    users = cache_users()
    return render_to_response('admin_sentry/index.html', 
                              {'results':qs, 'userlist': users,
                               'changes':ACTIONS.iterkeys(),
                               'filters':filters},
                              context_instance=RequestContext(request))

#@cache_page(300)
@login_required
def by_user(request, loguser):
    qs = get_user_logs(loguser)
    users = cache_users()
    return render_to_response('admin_sentry/user.html', {'results':qs,
                                                         'loguser':loguser,
                                                         'userlist':users},
                              context_instance=RequestContext(request))

#@cache_page(300)
@login_required
def by_changetype(request, action):
    qs = get_change_type(action)
    users = cache_users()
    return render_to_response('admin_sentry/changetype.html',
            {'results':qs, 'action':action,
             'userlist':users, 'changes':ACTIONS.iterkeys()},
             context_instance=RequestContext(request))

