from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

from admin_sentry import settings

ACTIONS = {1: 'Addition', 2: 'Change', 3: 'Deletion'}


@login_required
def index(request):
    qs = LogEntry.objects.all().order_by('-action_time')
    users = User.objects.all()
    return render_to_response('admin_sentry/index.html', 
                              {'results':qs, 'userlist': users,
                               'changes':ACTIONS.iterkeys()},
                              context_instance=RequestContext(request))

@login_required
def by_user(request, loguser):
    qs = LogEntry.objects.filter(user__username=loguser)
    return render_to_response('admin_sentry/user.html', {'results':qs,
                                                         'loguser':loguser},
                              context_instance=RequestContext(request))

