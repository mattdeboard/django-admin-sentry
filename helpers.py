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
from admin_sentry.models import ChangeLog


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

def get_old_info(sender, **kwargs):
    '''
    Takes a model instance and 
    '''
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)
    if content_type.model == 'changelog':
        return

    try:
        changelog = ChangeLog.objects.filter(model_class=str(content_type)).\
                    get(ref_id=instance.id)
    except:
        changelog = ChangeLog(ref_id=instance.id, model_class=str(content_type))
        changelog.save()
    
    for field in instance._meta.fields:
        changelog.prev_state[field.name] = field.value_from_object(instance)
    changelog.save()
    
#    cache_key = "lastattrs:%s:%s" % (content_type, instance.id)
#    cache.set(cache_key, old_attrs, 300)

def get_new_info(sender, **kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)
    if content_type.model == 'changelog':
        return


#    for field in instance._meta.fields:
#        changelog.setattr('%s_diff' % field.name,
#                          get_diff(field.value_from_object(instance),
#                                   changelog.prev_state[field.name]))

#    changelog.save()
    
    
pre_save.connect(get_old_info)
#post_save.connect(get_new_info)