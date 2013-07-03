import json
from datetime import timedelta
from time import time

import django.dispatch
from django.db import models
from django.dispatch import Signal
from django.utils import timezone

from controller.utils.time import heartbeat_expires

from . import settings


class BaseState(models.Model):
    data = models.TextField()
    metadata = models.TextField()
    last_seen_on = models.DateTimeField(null=True, help_text='Last time the state '
        'retrieval was successfull')
    last_try_on = models.DateTimeField(null=True, help_text='Last '
        'time the state retrieval operation has been executed')
    last_change_on = models.DateTimeField(null=True, help_text='Last time the state '
        'has change')
    
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
        return self.last_try_on + timedelta(seconds=freq)
    
    @classmethod
    def get_setting(cls, setting):
        name = cls.__name__.upper()
        return getattr(settings, "STATE_%s_%s" % (name, setting))
    
    @classmethod
    def store_glet(cls, obj, glet, get_data=lambda g: g.value):
        response = get_data(glet)
        field_name = cls.get_related_field_name()
        state, __ = cls.objects.get_or_create(**{field_name: obj})
        old_state = state.current
        now = timezone.now()
        state.last_try_on = now
        metadata = {'exception': str(glet._exception)}
        if response is not None:
            state.last_seen_on = now
            state.data = response.content
            metadata.update({
                'url': response.url,
                'headers': response.headers})
        else:
            state.data = ''
        state.metadata = json.dumps(metadata, indent=4)
        if old_state != state.current:
            state.last_change_on = now
        state.save()
        state.post_store_glet(obj, glet)
        return state
    
    def post_store_glet(self, obj, glet):
        pass
    
    @property
    def current(self):
        if not self.last_try_on:
            return 'nodata'
        cls = type(self)
        kwagrs = {
            'freq': cls.get_setting('SCHEDULE'),
            'expire_window': cls.get_setting('EXPIRE_WINDOW')}
        # TODO: NODATA when no running :)
        if self.last_seen_on and time() < heartbeat_expires(self.last_seen_on, **kwargs):
            # TODO: implement it first on the node
#            if self.metadata:
#                from datetime import datetime, timedelta
#                headers = json.loads(self.metadata).get('headers', False)
#                if headers:
#                    last_modified = headers.get('last-modified')
#                    last_modified = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
#                    date = headers.get('date')
#                    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
#                    if date - last_modified > timedelta(hours=1):
#                        return 'crashed'
            if self.data:
                try:
                    state = json.loads(self.data).get('state', 'unknown')
                except ValueError:
                    pass
            return 'unknown'
        return 'offline'
    
    def get_current_display(self):
        current = self.current
        for name,verbose in type(self).STATES:
            if name == current:
                return verbose
        return current
    
    @classmethod
    def get_url(cls, obj):
        URI = cls().get_setting('URI')
        node = getattr(obj, 'node', obj)
        return URI % {'mgmt_addr': node.mgmt_net.addr, 'object_id': obj.pk }


class NodeState(BaseState):
    STATES = (
        ('offline', 'OFFLINE'),
        ('debug', 'DEBUG'),
        ('safe', 'SAFE'),
        ('production', 'PRODUCTION'),
        ('failure', 'FAILURE'),
        ('unknown', 'UNKNOWN'),
        ('nodata', 'NO DATA'),
        ('crashed', 'CRASHED'),)
    
    node = models.OneToOneField('nodes.Node', related_name='state', primary_key=True)
    last_contact_on = models.DateTimeField(null=True, help_text='Last API pull '
        'received from this node.')
    soft_version = models.CharField(max_length=32, blank=True)
    
    def get_node(self):
        return self.node
    
    @classmethod
    def register_heartbeat(cls, node):
        node_state, __ = cls.objects.get_or_create(node=node)
        node_state.last_seen_on = timezone.now()
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
        ('nodata', 'NO DATA'),
        ('crashed', 'CRASHED'),
        ('registered', 'REGISTERED'),
        ('deployed', 'DEPLOYED'),
        ('started', 'STARTED'),
        ('fail_alloc', 'FAIL_ALLOC'),
        ('fail_deploy', 'FAIL_DEPLOY'),
        ('fail_start', 'FAIL_START'),)
    
    sliver = models.OneToOneField('slices.Sliver', related_name='state', primary_key=True)
    
    def get_node(self):
        return self.sliver.node
    
    @classmethod
    def get_related_field_name(cls):
        return 'sliver'


node_heartbeat = Signal(providing_args=["instance", "node"])
