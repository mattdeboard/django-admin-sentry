from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.admin.util import quote
from django.contrib.admin.models import LogEntry
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe

from directseo.seo.models import Configuration

import admin_sentry.diff_match_patch as diff


class ChangeLog(models.Model):
    '''
    '''
    ref_id = models.IntegerField()
    model_class = models.CharField(max_length=255)
    
    def set_content_type(self, content_type=None):
        self.content_type = content_type

    def get_content_type(self):
        return self.content_type
        
    def get_html_diff(self):
        return 
        
        
