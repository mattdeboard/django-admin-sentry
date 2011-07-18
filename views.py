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

@cache_page(300)
@login_required
def index(request):
    filters = []
    for filter_ in get_filters():
        filters.append(filter_(request))
    qs = LogEntry.objects.all().order_by("-action_time")
    
    if request.GET.get("user"):
        qs = qs.filter(user=request.GET["user"])

    if request.GET.get("action"):
        qs = qs.filter(action_flag=request.GET["action"])

    users = cache_users()
    return render_to_response('admin_sentry/index.html', 
                              {'results':qs, 'userlist': users,
                               'changes':ACTIONS.iterkeys(),
                               'filters':filters},
                              context_instance=RequestContext(request))