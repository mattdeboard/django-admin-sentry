from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from sawmill.helpers import *
from sawmill.forms import ASLogin
from sawmill.decorators import login_required

ACTIONS = {1: 'Addition', 2: 'Change', 3: 'Deletion'}

@cache_page(300)
@login_required(login_url='/sawmill/login/')
def index(request):
    filters = []
    for filter_ in get_filters():
        filters.append(filter_(request))
    qs = LogEntry.objects.all()
    
    if request.GET.get("user"):
        qs = get_user_logs(qs, request.GET["user"])

    if request.GET.get("action"):
        qs = get_action_logs(qs, request.GET["action"])

    users = cache_users()
    return render_to_response('sawmill/index.html', 
                              {'results':qs, 'userlist': users,
                               'changes':ACTIONS.iterkeys(),
                               'filters':filters},
                              context_instance=RequestContext(request))

def as_login(request):
    form = ASLogin()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/sawmill')
            else:
                messages.error(request, "You do not have proper permissions to "
                               "use this application. Ensure you are logging in"
                               " using your application's admin user/pass.")
        else:
            messages.error(request, "Invalid username or password. Ensure y"
                           "ou are logging in using your application's admi"
                           "n user/pass.", fail_silently=True)

    return render_to_response('sawmill/login.html', {'form': form},
                              context_instance=RequestContext(request))

def as_logout(request):
    logout(request)
    return render_to_response("sawmill/logout.html")
        