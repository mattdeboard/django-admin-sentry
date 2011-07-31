import itertools
import json

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth import login, authenticate, logout
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from sawmill.decorators import login_required
from sawmill.forms import ASLogin, ContentDropDown
from sawmill.helpers import *
from sawmill.models import InstanceLog
from sawmill.templatetags.helpertags import extract_user

ACTIONS = {1: 'Addition', 2: 'Change', 3: 'Deletion'}

@login_required(login_url='/sawmill/login/')
def index(request):
    # needs superuser verification
    filters = []
    for filter_ in get_filters():
        if filter_.label != "Object":
            filters.append(filter_(request))
    qs = LogEntry.objects.all()
    
    if request.GET.get("user"):
        qs = get_user_logs(qs, request.GET["user"])

    if request.GET.get("action"):
        qs = get_action_logs(qs, request.GET["action"])

    users = cache_users()
    return render_to_response('sawmill/index.html', 
                              {'results':qs,'changes':ACTIONS.iterkeys(),
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

@login_required(login_url='/sawmill/login')
def obj_overview(request):
    # needs superuser check
    form = ContentDropDown()
    filters = []
    query_dict = request.GET.copy()

    if request.is_ajax():
        if request.method == 'POST':
            model = request.POST['model']
            obj = request.POST['obj']
    else:
        model = query_dict['model']
        obj_id = query_dict['obj']

    for _filter in get_filters():
        if _filter.label == "Object":
            filters.append(_filter(request, model))
    time = 30
    cache_key = "instancelog:%s:%s:%s" % (model, obj_id, time)
    log_group = cache.get(cache_key)
    if not log_group:
        log_group = InstanceLog(model=model, obj_id=obj_id, timespan=time)
        cache.set(cache_key, log_group, SECONDS_TO_CACHE)
        
    editors = json.dumps([res[0] for res in log_group.get_editors()])
    edit_counts = json.dumps(log_group.get_editors())
    return render_to_response('sawmill/obj.html',
                              {'editors': editors,
                               'edit_counts': edit_counts,
                               'log_group': log_group,
                               'filters': filters,
                               'dropdown': form},
                              context_instance=RequestContext(request))

def notifications(request):
    if request.is_ajax():
        if request.method == 'POST':
            return HttpResponse("hi, thanks for visiting %s" % request.user)
            

