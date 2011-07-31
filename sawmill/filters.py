import itertools
import logging

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.html import escape

from sawmill.helpers import cache_users


class SinceLogin(object):
    '''
    Returns an HTML object that displays new items since a user's last
    login.
    
    '''
    actions = {1: "added", 2: "changed", 3: "deleted"}
    
    def __init__(self, filter, request):
        self.request = request
        self.filter = filter
        
    def render(self):
        results = self.filter.get_logs_since()
        rescount = results.count()

        if rescount:
            actionstr = "%s actions since your last login:" % rescount
        else:
            actionstr = "No activity since your last login."
        
        output = [
            """<ul class="changes-since-list"
                  rel="%s">
                  <li>%s</li>
            """ % (self.request.user.last_login, actionstr)]

        for result in results:
            output.append(
                """<li class="change-since">
                     %(user) %(action) %(strobj)
                     <span class="action-time">%(time)</span>
                   </li>
                """ %
                dict(user=result.user,
                     action=self.actions[result.action_flag],
                     strobj=result.object_repr,
                     time=str(result.action_time)))

        output.append('</ul>')
        return mark_safe('\n'.join(output))


class Widget(object):
    def __init__(self, filter, request):
        self.filter = filter
        self.request = request

    def get_query_string(self):
        return self.filter.get_query_string()


class TextWidget(Widget):
    def render(self, value, placeholder='', **kwargs):
        return mark_safe('<div class="filter-text"><p class="textfield"><input'
                         ' type="text" name="%(name)s" value="%(value)s" place'
                         'holder="%(placeholder)s"/></p><p class="submit"><inp'
                         'ut type="submit" class="search-submit" /></p></div>' %
                         dict(name=self.filter.get_query_param(),
                              value=escape(value),
                              placeholder=escape(placeholder or 'enter %s' % 
                                                 self.filter.label.lower()),
                              ))


class ChoiceWidget(Widget):
    def render(self, value, **kwargs):
        choices = self.filter.get_choices()
        query_string = self.get_query_string()
        column = self.filter.get_query_param()

        output = ['<ul class="%s-list filter-list" rel="%s">' %
                  (self.filter.column, column)]

        output.append('<li%(active)s><a href="%(query_string)s&amp;%(column)s="'
                      '>Any %(label)s</a></li>' %
                      dict(active=not value and ' class="active"' or '',
                           query_string=query_string,
                           label=self.filter.label,
                           column=column,))

        for key, val in choices.iteritems():
            key = unicode(key)

            if self.filter.label == "Object":
                count, val = val[0], val[1]
            else:
                count = self.filter.get_count(key)

            if len(val) >= 20:
                val = val[:17] + "..."
                
            output.append(
                """<li%(active)s rel="%(key)s">
                       <a href="%(query_string)s&amp;%(column)s=%(key)s">
                           %(value)s
                           <span class="count">%(count)s</span>
                       </a>
                   </li>
                """ % dict(active=value == key and ' class="active"' or '',
                           column=column,
                           key=key,
                           value=val,
                           query_string=query_string,
                           count=count,))
        output.append('</ul>')
        return mark_safe('\n'.join(output))


class ObjChoiceWidget(Widget):
    object_types = {25: "Social Link", 23: "Google Analytic",
                    21: "SEO Site Redirect", 20: "SEO Site",
                    19: "Configuration", 15: "Social Link", 14: "Index",
                    7: "Site", 3: "User", 2: "Group"}
    
    def render(self, value, **kwargs):
        choices = self.filter.get_choices()
        query_string = self.get_query_string()
        column = self.filter.get_query_param()
        output = ['<ul class="%s-list filter-list" rel="%s">' %
                  (self.filter.column, column)]

        for key, val in choices.iteritems():
            key = unicode(key)
            m, o = key.split('+')[0], key.split('+')[1]
            count, val = val[0], val[1]
            if len(val) >= 20:
                val = val[:17] + "..."
                    
            output.append(
                """<li%(active)s rel="%(key)s">
                       <a href="?&amp;model=%(model)s&amp;obj=%(obj)s">
                           %(value)s
                           <span class="count">%(count)s</span>
                       </a>
                   </li>
                """ % dict(active=value == key and ' class="active"' or '',
                           key=key,
                           model=m,
                           obj=o,
                           value=val,
                           count=count,))
        output.append('</ul>')
        return mark_safe('\n'.join(output))
                    

class BaseFilter(object):
    label = ''
    column = ''
    default = ''
    widget = ChoiceWidget
    show_label = True

    def __init__(self, request):
        self.request = request

    def is_set(self):
        return bool(self.get_value())

    def get_value(self):
        return self.request.GET.get(self.get_query_param(), self.default) or ''

    def get_query_param(self):
        return getattr(self, 'query_param', self.column)
    
    def get_query_string(self):
        column = self.column
        query_dict = self.request.GET.copy()
        if 'p' in query_dict:
            # Remove any pagination info in querystring
            del query_dict['p']
        if column in query_dict:
            del query_dict[column]
        return '?' + query_dict.urlencode()

    def get_choices(self):
        raise NotImplemented
        return
        
    def get_count(self):
        raise NotImplemented
        return

    def get_widget(self):
        return self.widget(self, self.request)

    def render(self):
        widget = self.get_widget()
        return widget.render(self.get_value())


class SinceFilter(BaseFilter):
    """
    Returns a queryset filtered on the requesting user's last_login property.
    
    """
    widget = SinceLogin
    
    def __init__(self, request):
        self.request = request
        self.user = request.user
        
    def get_logs_since(self):
        ll = self.user.last_login
        return LogEntry.objects.filter(action_time__gte=ll)\
                               .filter(user=self.user)\
                               .order_by('-action_time')

    def get_logs_count(self):
        return self.get_logs_since().count()

    def render(self):
        widget = self.get_widget()
        return widget.render()


class UserFilter(BaseFilter):
    label = 'User'
    column = 'user'
    
    def get_choices(self):
        userdict = SortedDict([(user.id, user.username) for user in cache_users()
                               if user.logentry_set.count()])
        return userdict

    def get_count(self, userid):
        return LogEntry.objects.filter(user=userid).count()


class ObjectFilter(BaseFilter):
    label = 'Object'
    column = 'object'
    widget = ObjChoiceWidget

    def __init__(self, request, ctype):
        self.request = request
        self.ctype = ctype

    def get_choices(self):
        query = """SELECT DISTINCT djl2.id, djl1.object_id, djl1.object_repr,
                                   djl1.content_type_id,
                                   COUNT(djl1.content_type_id) AS num_items
                   FROM django_admin_log AS djl1
                       INNER JOIN django_admin_log AS djl2
                       ON djl1.id=djl2.id
                   WHERE djl1.content_type_id = %s
                   GROUP BY djl1.object_repr, djl1.content_type_id
                   ORDER BY num_items DESC
                   LIMIT 20
                  """ % self.ctype
        logdict = SortedDict()
        results = LogEntry.objects.raw(query)
            
        
        for result in sorted(results, key=self.get_num_items):
            name, objid, num, mod = (result.object_repr, result.object_id,
                                     result.num_items, result.content_type_id)
            logdict.insert(0,"%s+%s" % (mod, objid), (num, name))

        return logdict
    
    def get_num_items(self, r):
        return r.num_items

    def get_count(self, index):
        return self.get_choices()[index][0]
    

class ActionFilter(BaseFilter):
    label = 'Action'
    column = 'action'

    def get_choices(self):
        return {1: 'Addition', 2: 'Change', 3: 'Deletion'}

    def get_count(self, action):
        return LogEntry.objects.filter(action_flag=action).count()

