from datetime import datetime
from time import time, mktime

from django.db import models

from nodes.models import Node


class NodeState(models.Model):
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    
    node = models.OneToOneField(Node, related_name='state')
    last_success_on = models.DateTimeField(null=True)
    last_retry_on = models.DateTimeField(auto_now=True)
    metadata = models.CharField(max_length=256)
    
    @classmethod
    def store_glet(cls, node, glet, get_data=lambda g: g.value):
        data = get_data(glet)
        state, created = cls.objects.get_or_create(node=node)
        if data is not None:
            state.last_success_on = datetime.now()
        state.metadata = {
            'exception': glet._exception,
            'value': get_data(glet), }
        state.save()
    
    @property
    def current(self):
        def heartbeat_expires(timestamp, freq=300, expire_window=200):
            return timestamp + freq * (expire_window / 1e2)
        
        if self.last_success_on and time() < heartbeat_expires(self.last_success_timestamp):
            return self.ONLINE
        return self.OFFLINE
    
    @property
    def last_success_timestamp(self):
        return mktime(self.last_success_on.timetuple())
