import itertools
import json
import math

from django import template
from django.contrib.admin.models import LogEntry
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import stringfilter
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
    qs = queryset.order_by('action_time')
    dates = []
    count = 1
    for date, group in itertools.groupby(qs, key=extract_date):
        dates.append([int(date.strftime("%s")) * 1000, len(list(group))])

    if dates:
        count = math.ceil(max(dates, key=get_max)[1] * 1.1)

    return {'points': dates, 'max_count': count}

def extract_date(log):
    '''
    Extract just the date portion of a datetime object.
    '''
    return log.action_time.date()

def extract_user(log):
    '''
    '''
    return log.user
    
def get_max(entry):
    return entry[1]

@register.filter
def max_value(data):
    '''
    Takes an iterator with nested iterators, each inner object containing a
    string and an int, and returns the inner obj with the largest int.
    '''
    return max(data, key=get_max)[1]
    
@register.filter
@stringfilter
def to_json(value):
    return json.dumps(value)

@register.filter
@stringfilter
def truncstr(value, l=10):
    '''
    Truncates a string to l characters, including three-period ellipsis.
    '''
    return value[:l-3] + '...'
    
