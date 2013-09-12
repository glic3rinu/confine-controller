import json
from datetime import timedelta
from time import time

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import Signal
from django.utils import timezone

from controller.utils.time import heartbeat_expires
from nodes.models import Node
from slices.models import Sliver

from . import settings


class State(models.Model):
    UNKNOWN = 'unknown'
    OFFLINE = 'offline'
    NODATA = 'nodata'
    BASE_STATES = (
        ('unknown', UNKNOWN),
        ('offline', OFFLINE),
        ('nodata', NODATA),
    )
    NODE_STATES = BASE_STATES + (
        ('production', 'PRODUCTION'),
        ('safe', 'SAFE'),
        ('debug', 'DEBUG'),
        ('failure', 'FAILURE'),
        ('crashed', 'CRASHED'),
    )
    SLIVER_STATES = BASE_STATES + (
        ('started', 'STARTED'),
        ('deployed', 'DEPLOYED'),
        ('registered', 'REGISTERED'),
        ('fail_start', 'FAIL_START'),
        ('fail_deploy', 'FAIL_DEPLOY'),
        ('fail_alloc', 'FAIL_ALLOC'),
    )
    STATES = tuple(set(BASE_STATES+NODE_STATES+SLIVER_STATES))
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    last_seen_on = models.DateTimeField(null=True,
            help_text='Last time the state retrieval was successfull')
    last_try_on = models.DateTimeField(null=True,
            help_text='Last time the state retrieval operation has been executed')
    last_contact_on = models.DateTimeField(null=True,
            help_text='Last API pull received from the node.')
    value = models.CharField(max_length=32, choices=STATES)
    metadata = models.TextField()
    data = models.TextField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return self.value
    
    @property
    def last_change_on(self):
        return self.history.all().order_by('-date')[0].date
    
    @property
    def soft_version(self):
        return json.loads(self.data).get('soft_version', '')
    
    @property
    def current(self):
        expiration_time = heartbeat_expires(self.last_try_on, freq=settings.STATE_SCHEDULE,
                expire_window=settings.STATE_EXPIRE_WINDOW)
        if not self.last_try_on or time() > expiration_time:
            return self.NODATA
        return self.value
    
    @classmethod
    def store_glet(cls, obj, glet, get_data=lambda g: g.value):
        state, __ = obj.state.get_or_create(object_id=obj.id)
        old_state = state.current
        now = timezone.now()
        state.last_try_on = now
        metadata = {
            'exception': str(glet._exception) if glet._exception else None
        }
        response = get_data(glet)
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
            state.history.create(state=state.current)
        state.save()
        return state
    
    @classmethod
    def register_heartbeat(cls, obj):
        state, __ = obj.state.get_or_create(object_id=obj.id)
        state.last_seen_on = timezone.now()
        state.last_contact_on = state.last_seen_on
        state.save()
        node_heartbeat.send(sender=cls, node=obj.node or obj)


node_heartbeat = Signal(providing_args=["instance", "node"])


for model in [Node, Sliver]:
    model.add_to_class('state', generic.GenericRelation('state.State'))


class StateHistory(models.Model):
    state = models.ForeignKey(State)
    value = models.CharField(max_length=32, choices=State.STATES)
    date = models.DateTimeField(auto_now_add=True)
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        return self.value
