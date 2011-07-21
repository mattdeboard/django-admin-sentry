import json

from django import template
from django.contrib.admin.models import LogEntry
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import SortedDict

from sawmill.conf import USER_PROFILE_URL
from sawmill.helpers import cache_users

register = template.Library()

actions = {1: 'addition', 2: 'change', 3: 'deletion'}

@register.filter
def trans_actions(action):
    try:
        res = actions[action]
    except:
        res = None
    return res

@register.filter
def abbrev(action):
    return actions[action][0].upper()

@register.filter
def timesince(value):
    '''
    Copied from django-sentry v1.6.2

    github.com/dcramer/django-sentry
    '''
    import datetime
    from django.template.defaultfilters import timesince
    if not value:
        return 'Never'
    if value < datetime.datetime.now() - datetime.timedelta(days=5):
        return value.date()
    value = (' '.join(timesince(value).split(' ')[0:2])).strip(',')
    if value == '0 minutes':
        return 'Just now'
    if value == '1 day':
        return 'Yesterday'
    return value + ' ago'

@register.filter
def get_user_admin_url(value):
    '''
    Given a username (`value`), return a string containing an absolute
    path to the user's admin profile.
    '''
    users = cache_users()
    try:
        user = users.get(username=value)
        uid = str(user.id)
    except ObjectDoesNotExist:
        uid = '#'
        
    return "%s/%s" % (USER_PROFILE_URL, uid)
    
@register.filter
def log_dates(queryset):
    '''
    Given a LogEntry queryset, return a list of 3-tuples. Each 3-tuple
    contains (year, month, day) of the LogEntry's creation date. No
    duplicates permitted.
    '''
    at = 'action_time'
    qs = queryset.filter(action_time__isnull=False).distinct().values(at)
    dates = []
    for entry in qs:
        if entry['action_time'] not in dates:
            dates.append(entry[at])
            
    return {'points':[[int(date.strftime("%s")) * 1000,
                       LogEntry.objects.filter(action_time=date).count()] for \
                      date in dates],
            'dates': [int(date.strftime("%s")) * 1000 for date in dates]}

@register.filter
def to_json(value):
    return json.dumps(value)

@register.filter
def first(iterable):
    return iterable[0]

def last(iterable):
    return iterable[-1]

