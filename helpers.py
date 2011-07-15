from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.core.cache import cache

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
                continue
            filters.append(filter_)
        _FILTER_CACHE = filters
        for f in _FILTER_CACHE:
            yield f

def get_change_type(action):
    cache_key = 'adminlog:change-%s' % action
    results = cache.get(cache_key)
    a = {'addition': 1, 'update': 2, 'deletion': 3}

    if not results:
        results = LogEntry.objects.filter(action_flag=a[action])
        cache.set

    return results

def get_user_logs(user):
    cache_key = 'adminlog:%s-logs' % user
    results = cache.get(cache_key)

    if not results:
        results = LogEntry.objects.filter(user__username=user)
        cache.set(cache_key, results, MINUTES_TO_CACHE * 5)

    return results

def cache_users():
    cache_key = 'adminlog:allusers'
    users = cache.get(cache_key)

    if not users:
        users = User.objects.all()
        cache.set(cache_key, users, MINUTES_TO_CACHE * 60)

    return users
