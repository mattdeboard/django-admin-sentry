import itertools
import logging

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.html import escape

from sawmill.helpers import cache_users


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
                
            output.append('<li%(active)s rel="%(key)s"><a href="%(query_string)'
                          's&amp;%(column)s=%(key)s">%(value)s<span class="'
                          'count">%(count)s</span></a></li>' %
                          dict(active=value == key and ' class="active"' or '',
                               column=column,
                               key=key,
                               value=val,
                               query_string=query_string,
                               count=count,))
        output.append('</ul>')
        return mark_safe('\n'.join(output))


class ObjChoiceWidget(Widget):
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
                    
            output.append('<li%(active)s rel="%(key)s"><a href="?&amp;model=%(m'
                          'odel)s&amp;obj=%(obj)s">%(value)s<span class="c'
                          'ount">%(count)s</span></a></li>' %
                          dict(active=value == key and ' class="active"' or '',
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
    model = '' # model id
    obj = '' # object id

    # def get_choices(self):
    #     logdict = SortedDict([])
    #     logs = LogEntry.objects.all()
    #     res = [(len(list(group)), obj) for obj, group in itertools.groupby\
    #            (logs, key=self.get_objs)]
    #     # sort the list of results, then reverse it to get them in order by
    #     # number of entries. Then, store the value of the top 10 entries.
    #     # Then, reverse THAT list to get them in reverse order, so they're
    #     # stored in the SortedDict in descending order. :)
    #     res.sort()
    #     res.reverse()
    #     res = res[:10]
    #     res.reverse()
    #     for pair in res:
    #         log = LogEntry.objects.filter(object_repr=pair[1])[0]
    #         logdict.insert(0, "%s+%s" % (log.content_type.id, log.object_id),
    #                        pair)
            
    #     return logdict

    def get_choices(self):
        logdict = SortedDict()
        results = LogEntry.objects.raw(
            """SELECT DISTINCT djl2.id, djl1.object_id, djl1.object_repr,
                               djl1.content_type_id,
                               COUNT(djl1.content_type_id) AS num_items
               FROM django_admin_log AS djl1
                   INNER JOIN django_admin_log AS djl2
                   ON djl1.id=djl2.id
               GROUP BY djl1.object_repr, djl1.content_type_id
               ORDER BY num_items
            """)
        
        for result in results:
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

