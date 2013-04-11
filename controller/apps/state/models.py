import json
from datetime import timedelta
from time import time, mktime

import django.dispatch
from django.db import models
from django.dispatch import Signal
from django.utils.timezone import now

from . import settings


class BaseState(models.Model):
    data = models.TextField()
    metadata = models.TextField()
    last_seen_on = models.DateTimeField(null=True, help_text='Last time the state '
        'retrieval was successfull')
    last_try_on = models.DateTimeField(auto_now=True, null=True, help_text='Last '
        'time the state retrieval operation has been executed')
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return str(getattr(self, type(self).get_related_field_name())) + ' state'
    
    @classmethod
    def get_related_field_name(cls):
        raise NotImplementedError
    
    @classmethod
    def get_related_model(cls):
        field_name = cls.get_related_field_name()
        return cls._meta.get_field(field_name).rel.to
    
    @property
    def next_retry_on(self):
        freq = type(self).get_setting('SCHEDULE')
        time = self.last_try_on + timedelta(seconds=freq)
        return time.strftime("%B %d, %Y, %I:%M %p.")
    
    @classmethod
    def get_setting(cls, setting):
        name = cls.__name__.upper()
        return getattr(settings, "STATE_%s_%s" % (name, setting))
    
    @classmethod
    def store_glet(cls, obj, glet, get_data=lambda g: g.value):
        response = get_data(glet)
        field_name = cls.get_related_field_name()
        state, created = cls.objects.get_or_create(**{field_name: obj})
        metadata = {'exception': str(glet._exception)}
        if response is not None:
            state.last_seen_on = now()
            state.data = response.content
            metadata.update({
                'url': response.url,
                'headers': response.headers})
        state.metadata = json.dumps(metadata, indent=4)
        state.save()
        state.post_store_glet(obj, glet)
        return state
    
    def post_store_glet(self, obj, glet):
        pass
    
    @property
    def current(self):
        cls = type(self)
        freq = cls.get_setting('SCHEDULE')
        expire_window = cls.get_setting('EXPIRE_WINDOW')
        
        def heartbeat_expires(timestamp, freq=freq, expire_window=expire_window):
            return timestamp + freq * (expire_window / 1e2)
        
        if self.last_seen_on and time() < heartbeat_expires(self.last_seen_timestamp):
            if self.data:
                try:
                    return json.loads(self.data).get('state', 'unknown')
                except ValueError:
                    pass
            return 'unknown'
        return 'offline'
    
    @property
    def last_seen_timestamp(self):
        return mktime(self.last_seen_on.timetuple())
    
    def get_current_display(self):
        current = self.current
        for name,verbose in type(self).STATES:
            if name == current:
                return verbose
        return current


class NodeState(BaseState):
    STATES = (
        ('offline', 'OFFLINE'),
        ('debug', 'DEBUG'),
        ('safe', 'SAFE'),
        ('production', 'PRODUCTION'),
        ('failure', 'FAILURE'),
        ('unknown', 'UNKNOWN'),)
    
    node = models.OneToOneField('nodes.Node', related_name='state')
    last_contact_on = models.DateTimeField(null=True, help_text='Last API pull '
        'received from this node.')
    soft_version = models.CharField(max_length=32, blank=True)
    
    def get_node(self):
        return self.node
    
    @classmethod
    def register_heartbeat(cls, node):
        node_state, new = cls.objects.get_or_create(node=node)
        node_state.last_seen_on = now()
        node_state.last_contact_on = node_state.last_seen_on
        node_state.save()
        node_heartbeat.send(sender=cls, node=node)
    
    @classmethod
    def get_related_field_name(cls):
        return 'node'
    
    def post_store_glet(self, obj, glet):
        try:
            self.soft_version = json.loads(self.data).get('soft_version', '')
        except ValueError:
            pass
        else:
            self.save()


class SliverState(BaseState):
    STATES = (
        ('offline', 'OFFLINE'),
        ('unknown', 'UNKNOWN'),
        ('registered', 'REGISTERED'),
        ('deployed', 'DEPLOYED'),
        ('started', 'STARTED'),
        ('fail_alloc', 'FAIL_ALLOC'),
        ('fail_deploy', 'FAIL_DEPLOY'),
        ('fail_start', 'FAIL_START'),)
    
    sliver = models.OneToOneField('slices.Sliver', related_name='state')
    
    def get_node(self):
        return self.sliver.node
    
    @classmethod
    def get_related_field_name(cls):
        return 'sliver'


node_heartbeat = Signal(providing_args=["instance", "node"])
