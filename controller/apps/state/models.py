import json
from datetime import timedelta
from time import time

from django.db import models
from django.dispatch import Signal
from django.utils import timezone

from controller.utils.time import heartbeat_expires

from . import settings


class BaseState(models.Model):
    UNKNOWN = 'unknown'
    OFFLINE = 'offline'
    NODATA = 'nodata'
    STATES = (
        ('unknown', 'UNKNOWN'),
        ('offline', 'OFFLINE'),
        ('nodata', 'NO DATA'),
    )
    data = models.TextField()
    metadata = models.TextField()
    last_seen_on = models.DateTimeField(null=True,
            help_text='Last time the state retrieval was successfull')
    last_try_on = models.DateTimeField(null=True,
            help_text='Last time the state retrieval operation has been executed')
    last_change_on = models.DateTimeField(null=True,
            help_text='Last time the state has change')
    add_date = models.DateTimeField(auto_now_add=True)
    
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
        metadata = {'exception': str(glet._exception) if glet._exception else None}
        if response is not None:
            state.last_seen_on = now
            if response.status_code != 304:
                state.data = response.content
            metadata.update({
                'url': response.url,
                'headers': response.headers,
                'status_code': response.status_code
            })
        else:
            state.data = ''
        state.metadata = json.dumps(metadata, indent=4)
        if old_state != state.current and old_state != BaseState.NODATA:
            state.last_change_on = now
        state.save()
        state.post_store_glet(obj, glet)
        return state
    
    def post_store_glet(self, obj, glet):
        pass
    
    @property
    def current(self):
        cls = type(self)
        kwargs = {
            'freq': cls.get_setting('SCHEDULE'),
            'expire_window': cls.get_setting('EXPIRE_WINDOW')
        }
        if not self.last_try_on or time() > heartbeat_expires(self.last_try_on, **kwargs):
            return self.NODATA
        
        if self.last_seen_on and time() < heartbeat_expires(self.last_seen_on, **kwargs):
            if self.data:
                try:
                    return json.loads(self.data).get('state', self.UNKNOWN)
                except ValueError:
                    pass
            return self.UNKNOWN
        return self.OFFLINE
    
    def get_current_display(self):
        current = self.current
        for name,verbose in type(self).STATES:
            if name == current:
                return verbose
        return current
    
    def get_url(self):
        URI = type(self).get_setting('URI')
        node = self.get_node()
        return URI % { 'mgmt_addr': node.mgmt_net.addr, 'object_id': self.pk }
    
    @property
    def related_object(self):
        field = self.get_related_field_name()
        return getattr(self, field)


class NodeState(BaseState):
    PRODUCTION = 'production'
    SAFE = 'safe'
    DEBUG = 'debug'
    FAILURE = 'failure'
    CRASHED = 'crashed'
    STATES = (
        ('production', 'PRODUCTION'),
        ('safe', 'SAFE'),
        ('debug', 'DEBUG'),
        ('failure', 'FAILURE'),
        ('crashed', 'CRASHED'),
    ) + BaseState.STATES
    
    node = models.OneToOneField('nodes.Node', related_name='state', primary_key=True)
    last_contact_on = models.DateTimeField(null=True,
            help_text='Last API pull received from this node.')
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
    
    @property
    def current(self):
        """ node is crashed if we do not receive node heartbeats beyond a timeout """
        state = super(NodeState, self).current
        if state not in [self.OFFLINE, self.NODATA]:
            # offline and nodata are worst than crashed :)
            timeout_expire = timezone.now()-settings.STATE_NODE_PULL_TIMEOUT
            if self.add_date < timeout_expire:
                if not self.last_contact_on or self.last_contact_on < timeout_expire:
                    return self.CRASHED
        return state


class SliverState(BaseState):
    STATES = (
        ('started', 'STARTED'),
        ('deployed', 'DEPLOYED'),
        ('registered', 'REGISTERED'),
        ('fail_start', 'FAIL_START'),
        ('fail_deploy', 'FAIL_DEPLOY'),
        ('fail_alloc', 'FAIL_ALLOC'),
    ) + BaseState.STATES
    
    sliver = models.OneToOneField('slices.Sliver', related_name='state', primary_key=True)
    
    def get_node(self):
        return self.sliver.node
    
    @classmethod
    def get_related_field_name(cls):
        return 'sliver'


node_heartbeat = Signal(providing_args=["instance", "node"])
