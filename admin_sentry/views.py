from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

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
        qs = get_user_logs(qs, request.GET["user"])

    if request.GET.get("action"):
        qs = get_action_logs(qs, request.GET["action"])

    users = cache_users()
    return render_to_response('admin_sentry/index.html', 
                              {'results':qs, 'userlist': users,
                               'changes':ACTIONS.iterkeys(),
                               'filters':filters},
                              context_instance=RequestContext(request))

def as_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/admin_sentry')
            else:
                messages.error(request, "You do not have proper permissions to "
                               "use this application. Ensure you are logging in"
                               " using your application's admin user/pass.")
            else:
                messages.error(request, "Invalid username or password. Ensure y"
                               "ou are logging in using your application's admi"
                               "n user/pass.")

    return render_to_response('admin_sentry/login.html')


        