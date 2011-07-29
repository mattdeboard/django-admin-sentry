import datetime
import itertools
import math

from django.contrib.admin.models import LogEntry


class ConstraintError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
        

class BoundedList(list):
    '''
    A list that will only accept new members while the list's length is
    less than a specified amount.
    
    '''
    def __init__(self, length):
        super(BoundedList, self).__init__()
        self.len = length

    def append(self, thing, silent=False):
        '''
        BoundedList.append(thing[, silent=False]) ->
        Appends 'thing' to an instance of BoundedList, iff. len(self) is
        less than self.len. If silent == True, the append process will
        simply stop when the limit is reached. If False, it will raise
        an exception.
        
        '''
        warning = "BoundedList is constrained to length %s." % self.len
        if len(self) < self.len:
            super(BoundedList, self).append(thing)
        elif silent == True:
            return
        else:
            raise ConstraintError(warning)
                

class InstanceLog(object):
    '''
    InstanceLog(obj_id) -> Returns instance representing the information
    in a group of log entries for a common model instance.

    '''
    def __init__(self, model=None, obj_id=None, timespan=None):
        if obj_id:
            self.obj_id = obj_id
            self.query = LogEntry.objects.filter(object_id=self.obj_id)\
                                         .filter(content_type__id=model)\
                                         .order_by('user')
        else:
            q = LogEntry.objects.filter(content_type__id=model)\
                                .order_by('user')
            self.query = q.filter(object_id=q[0].object_id)

        self.timespan = timespan
        self.count, self.name, self.name2 = self.get_obj_info()
        
    def get_obj_info(self):
        name = self.query[0].object_repr.split(' -- ')
        if len(name) == 1:
            name.append(' ')
        return (self.query.count(), name[0], name[1])
                
    def get_editors(self):
        return [(str(user), len(list(group))) for user, group in itertools\
                .groupby(self.query, key=self._get_user)]

    def _get_user(self, logitem):
        try:
            res = logitem.user
        except:
            res = None
        return res

    def _sort_by_user(self, t):
        return t[1]

    def first_edit(self):
        return self.query[0].action_time

    def most_recent_edit(self):
        return self.query[self.count-1].action_time

    def num_edits_by(self, reverse=True):
        # returns username of user who has contributed most revisions to
        # the instance. if reverse == True, returns username of who has
        # contributed LEAST.
        res = self.get_editors()
        res.sort(key=self._sort_by_user)
        if reverse:
            res.reverse()
        return res[0][0]

    def log_dates(self):
        '''
        
        '''
        at = 'action_time'
        dates = []
        date_query = self.query.order_by('-action_time')
        datelist = BoundedList(self.timespan)
        for date, g in itertools.groupby(date_query, key=self._extract_date):
            datelist.append([int(date.strftime("%s")) * 1000, len(list(g))],
                            silent=True)

        return {'points': datelist, 'bl_count': len(datelist)}

    def _get_max_date(self, entry):
        return entry[1]

    def _extract_date(self, log):
        return log.action_time.date()

    def editors(self):
        return [u[0] for u in self.get_editors()]

    def admin_url(self):
        return self.query[0].get_admin_url()
