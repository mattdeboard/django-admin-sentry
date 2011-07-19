from django.contrib import admin
from django.contrib.admin.models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    list_filter = ['user', 'object_repr', 'action_time']
    list_display = ('action_time', 'user', 'action_flag', 'change_message',
                    'object_repr')
    search_fields = ['object_repr', 'user']
    fieldsets = (
            (None, {'fields': (('user', 'content_type', 'object_repr'), 
                               'action_time')}),)
    readonly_fields = ('user', 'content_type', 'object_repr', 'action_time') 

    def queryset(self, request):
        qs = super(LogEntryAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group__in=request.user.groups.all())


admin.site.register(LogEntry, LogEntryAdmin)
