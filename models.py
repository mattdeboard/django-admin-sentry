from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.admin.util import quote
from django.contrib.admin.models import LogEntry
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe


class LogProxy(object):
    '''
    Represents a LogEntry instance without needing to rewrite the core 
    LogEntry model. Instantiate with the id of a LogEntry instance, e.g.:

        my_entry = LogProxy(3)

    All attributes & methods of the LogEntry with id==3 will be accessible
    via e.g.:
        
        my_entry.entry.user | my_entry.object_repr

    etc.
    '''
        
    def get_action(self):
        # Values for this dict pulled from django.contrib.admin.models.LogEntry
        actions = {0: 'Addition', 1: 'Change', 2: 'Deletion'}
        return actions[self.entry.action_flag]


class FilterValue(models.Model):
    FILTER_KEYS = (
            ('user', _('server name')),
            ('action', _('action')),
            ('object', _('object')),
    )

    key = models.CharField(choices=FILTER_KEYS, max_length=32)
    value = models.CharField(max_length=200)
