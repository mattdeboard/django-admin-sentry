import copy
import datetime
import hashlib
import logging

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save

import admin_sentry.diff_match_patch as diff
from admin_sentry import conf


MINUTES_TO_CACHE = 60
_FILTER_CACHE = None

def get_filters():
    global _FILTER_CACHE

    if _FILTER_CACHE is None:
        filters = []
        for filter_ in conf.FILTERS:
            module_name, class_name = filter_.rsplit('.', 1)
            try:
                module = __import__(module_name, {}, {}, class_name)
                filter_ = getattr(module, class_name)
            except Exception:
                logger = logging.getLogger('as_errors')
                logger.exception("Unable to import %s" % (filter_,))
                continue
            filters.append(filter_)
        _FILTER_CACHE = filters
    for f in _FILTER_CACHE:
        yield f

def get_action_logs(queryset, action):
    cache_key = 'adminlog:action-%s' % action
    results = cache.get(cache_key)

    if not results:
        # `action` comes in as a string from request.GET, so must force
        # to int.
        results = queryset.filter(action_flag=int(action))
        cache.set

    return results

def get_user_logs(queryset, user):
    cache_key = 'adminlog:%s-logs' % user
    results = cache.get(cache_key)

    if not results:
        # `user` comes in as a string from request.GET, so must force to
        # int.
        results = queryset.filter(user=int(user))
        cache.set(cache_key, results, MINUTES_TO_CACHE * 5)

    return results

def cache_users():
    cache_key = 'adminlog:allusers'
    users = cache.get(cache_key)

    if not users:
        users = User.objects.all()
        cache.set(cache_key, users, MINUTES_TO_CACHE * 60)

    return users

def get_diff(sender, **kwargs):
    '''
    Depends on Google's diff_match_patch script.
    http://code.google.com/p/google-diff-match-patch
    '''
    
    return diff.diff_main(old, new)