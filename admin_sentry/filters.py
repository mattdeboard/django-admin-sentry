from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.html import escape

from admin_sentry.helpers import cache_users


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
            if len(val) >= 23:
                val = val[:20] + "..."
            output.append('<li%(active)s rel="%(key)s"><a href="%(query_string)'
                          's&amp;%(column)s=%(key)s">%(value)s</a></li>' %
                          dict(active=value == key and ' class="active"' or '',
                               column=column,
                               key=key,
                               value=val,
                               query_string=query_string,))
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
        from admin_sentry import FilterValue
        return SortedDict((l, l) for l in
                FilterValue.objects.filter(key=self.column).values_list('value',
                    flat=True).order_by('value'))

    def get_widget(self):
        return self.widget(self, self.request)

    def render(self):
        widget = self.get_widget()
        return widget.render(self.get_value())


class UserFilter(BaseFilter):
    label = 'User'
    column = 'user'
    
    def get_choices(self):
        userdict = SortedDict([])
        for user in cache_users():
            if user.logentry__set.count():
                userdict.insert(0, user.id, user.username)
        return userdict


class ObjectFilter(BaseFilter):
    label = 'Object'
    column = 'object_repr'


class ActionFilter(BaseFilter):
    label = 'Action'
    column = 'action'

    def get_choices(self):
        return {1: 'Addition', 2: 'Change', 3: 'Deletion'}

