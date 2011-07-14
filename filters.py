from django.contrib.admin.models import LogEntry


class BaseFilter(object):
    label = ''
    column = ''
    default = ''

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
        return '?' + query_dict.urlencode()

    def get_choices(self):
        from admin_sentry import FilterValue
        return SortedDict((l, l) for l in
                FilterValue.objects.filter(key=self.column).values_list('value',
                    flat=True).order_by('value'))


class UserFilter(BaseFilter):
    label = 'User'
    column = 'user'


class ObjectFilter(BaseFilter):
    label = 'Object'
    column = 'object_repr'


class ActionFilter(BaseFilter):
    label = 'Action'
    column = 'action_flag'

    def get_action(self, instance):
        actions = {0: 'Addition', 1: 'Change', 2: 'Deletion'}
        return actions[instance.action_flag]

