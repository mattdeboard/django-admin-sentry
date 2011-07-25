import itertools

from django.contrib.admin.models import LogEntry


class InstanceLog(object):
    '''
    InstanceLog(obj_id) -> Returns instance representing the information
    in a group of log entries for a common model instance.

    '''
    def __init__(self, obj_id=None):
        self.obj_id = obj_id
        self.query = LogEntry.objects.filter(id=self.obj_id)
        self.name, self.count = self.get_obj_info()
        
    def get_obj_info(self):
        return (self.query.count(), self.query[0].object_repr.split(' -- ')[0])
                
    def get_editors(self):
        return [(user, len(list(group))) for user, group in itertools.groupby\
                (self.query, key=self._get_user)]

    def _get_user(self, logitem):
        return logitem.user

        
    

    
        
        
