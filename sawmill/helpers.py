import logging

from django.contrib.auth.models import User
from django.core.cache import cache

from sawmill import conf


MINUTES_TO_CACHE = 60
_FILTER_CACHE = None

def get_filters(*args, **kwargs):
    '''
    Retrieve and import filters from conf.py.

    args is any of: User, Action, Object.
    
    '''
    global _FILTER_CACHE

    if not args:
        args = ['User', 'Action']

    if 'Object' in args:
        try:
            ctype = kwargs['content_type']
        except:
            logger = logging.getLogger('as_errors')
            logger.exception("No object ID was passed in to get_filters.")
            continue

    
    if _FILTER_CACHE is None:
        filters = []
        for filter_ in conf.FILTERS:
            for f in args:
                if f in filter_:
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
        #cache.set(cache_key, results, MINUTES_TO_CACHE * 60)

    return results

def get_user_logs(queryset, user):
    cache_key = 'adminlog:%s-logs' % user
    results = cache.get(cache_key)

    if not results:
        # `user` comes in as a string from request.GET, so must force to
        # int.
        results = queryset.filter(user=int(user))
        cache.set(cache_key, results, MINUTES_TO_CACHE * 60)

    return results

def cache_users():
    cache_key = 'adminlog:allusers'
    users = cache.get(cache_key)

    if not users:
        users = User.objects.all()
        cache.set(cache_key, users, MINUTES_TO_CACHE * 1)

    return users
