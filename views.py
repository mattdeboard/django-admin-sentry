

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from admin_sentry import settings

ACTIONS = {1: 'Addition', 2: 'Change', 3: 'Deletion'}
MINUTES_TO_CACHE = 60

@cache_page(300)
@login_required
def index(request):
    from admin_sentry.filters import UserFilter, ObjectFilter, ActionFilter
    qs = LogEntry.objects.all().order_by('-action_time')
    users = cache_users()
    filters = [UserFilter]
    return render_to_response('admin_sentry/index.html', 
                              {'results':qs, 'userlist': users,
                               'changes':ACTIONS.iterkeys()},
                              context_instance=RequestContext(request))

@cache_page(300)
@login_required
def by_user(request, loguser):
    qs = get_user_logs(loguser)
    users = cache_users()
    return render_to_response('admin_sentry/user.html', {'results':qs,
                                                         'loguser':loguser,
                                                         'userlist':users},
                              context_instance=RequestContext(request))

@cache_page(300)
@login_required
def by_changetype(request, action):
    qs = get_change_type(action)
    users = cache_users()
    return render_to_response('admin_sentry/changetype.html',
            {'results':qs, 'action':action,
             'userlist':users, 'changes':ACTIONS.iterkeys()},
             context_instance=RequestContext(request))

def get_change_type(action):
    cache_key = 'adminlog:change-%s' % action
    results = cache.get(cache_key)
    a = {'addition': 1, 'update': 2, 'deletion': 3}

    if not results:
        results = LogEntry.objects.filter(action_flag=a[action])
        cache.set

    return results

def get_user_logs(user):
    cache_key = 'adminlog:%s-logs' % user
    results = cache.get(cache_key)

    if not results:
        results = LogEntry.objects.filter(user__username=user)
        cache.set(cache_key, results, MINUTES_TO_CACHE * 5)

    return results

def cache_users():
    cache_key = 'adminlog:allusers'
    users = cache.get(cache_key)

    if not users:
        users = User.objects.all()
        cache.set(cache_key, users, MINUTES_TO_CACHE * 60)

    return users
