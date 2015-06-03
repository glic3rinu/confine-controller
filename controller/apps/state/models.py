import json
import functools
from datetime import datetime, timedelta
from time import time

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import Signal
from django.utils import timezone
from django.utils.functional import cached_property
from django_transaction_signals import defer

from controller.utils.functional import cached
from controller.utils.time import heartbeat_expires as heartbeatexpires
from nodes.models import Node, NodeApi
from slices.models import Sliver

from . import settings
from .helpers import extract_node_software_version
from .tasks import get_state


class State(models.Model):
    UNKNOWN = 'unknown'
    OFFLINE = 'offline'
    NODATA = 'nodata'
    FAILURE = 'failure'
    CRASHED = 'crashed'
    BASE_STATES = (
        (UNKNOWN, 'UNKNOWN'),
        (OFFLINE, 'OFFLINE'),
        (NODATA, 'NODATA'),
    )
    NODE_STATES = BASE_STATES + (
        ('production', 'PRODUCTION'),
        ('safe', 'SAFE'),
        ('debug', 'DEBUG'),
        (FAILURE, 'FAILURE'),
        (CRASHED, 'CRASHED'),
    )
    SLIVER_STATES = BASE_STATES + (
        ('started', 'STARTED'),
        ('deployed', 'DEPLOYED'),
        ('registered', 'REGISTERED'),
        ('fail_start', 'FAIL_START'),
        ('fail_deploy', 'FAIL_DEPLOY'),
        ('fail_allocate', 'FAIL_ALLOCATE'),
    )
    STATES = tuple(set(BASE_STATES+NODE_STATES+SLIVER_STATES))
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    last_seen_on = models.DateTimeField(null=True,
            help_text='Last time the state retrieval was successfull.')
    last_try_on = models.DateTimeField(null=True,
            help_text='Last time the state retrieval operation has been executed.')
    last_contact_on = models.DateTimeField(null=True,
            help_text='Last API pull of this resource received from the node.')
    value = models.CharField(max_length=32, choices=STATES)
    metadata = models.TextField()
    data = models.TextField()
    add_date = models.DateTimeField(auto_now_add=True)
    ssl_verified = models.BooleanField('verified', default=False,
            help_text='Whether the SSL certificate could be verified on node '
                      'API retrieval.')
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return self.value
    
    def save(self, *args, **kwargs):
        # backwards compatibility (#385)
        if self.value == 'fail_alloc':
            self.value = 'fail_allocate'
        super(State, self).save(*args, **kwargs)
    
    @property
    @cached
    def last_change_on(self):
        last_state = self.last
        return last_state.start if last_state else None
    
    @property
    @cached
    def heartbeat_expires(self):
        schedule = settings.STATE_SCHEDULE
        window = settings.STATE_EXPIRE_WINDOW
        return functools.partial(heartbeatexpires, freq=schedule, expire_window=window)
    
    @property
    @cached
    def last(self):
        history = self.history.all().order_by('-start')
        return history[0] if history else None
    
    @property
    @cached
    def current(self):
        if not self.last_try_on or time() > self.heartbeat_expires(self.last_try_on):
            return self.NODATA
        return self.value
    
    @property
    @cached
    def next_retry_on(self):
        freq = settings.STATE_SCHEDULE
        return self.last_try_on + timedelta(seconds=freq)
    
    @classmethod
    def store_glet(cls, obj, glet, get_data=lambda g: g.value):
        state = obj.state
        now = timezone.now()
        state.last_try_on = now
        metadata = {
            'exception': str(glet._exception) if glet._exception else None
        }
        response = get_data(glet)
        if response is not None:
            state.last_seen_on = now
            state.ssl_verified = response.headers.pop('ssl_verified', False)
            if response.status_code != 304:
                state.data = response.text
                if isinstance(obj, Node):
                    state._store_soft_version()
            metadata.update({
                'url': response.url,
                # CaseInsensitiveDict not JSON serializable (#468)
                'headers': dict(response.headers),
                'status_code': response.status_code,
                'ssl_verified': state.ssl_verified,
            })
            state._compute_current()
        else:
            # Exception, we assume OFFLINE state
            state.data = ''
            state.value = State.OFFLINE
        state.metadata = json.dumps(metadata, indent=4)
        state.history.store()
        state.save()
        return state
    
    @classmethod
    def register_heartbeat(cls, obj):
        state = obj.state
        state.last_seen_on = timezone.now()
        state.last_contact_on = state.last_seen_on
        state.save()
        if state.value in (cls.CRASHED, cls.OFFLINE):
            opts = type(obj)._meta
            module = '%s.%s' % (opts.app_label, opts.object_name)
            defer(get_state.delay, module, ids=[obj.pk], lock=False)
        node_heartbeat.send(sender=cls, node=obj.state.get_node())
    
    def _compute_current(self):
        if (not self.last_seen_on and time() > self.heartbeat_expires(self.add_date) or
                self.last_seen_on and time() > self.heartbeat_expires(self.last_seen_on)):
            self.value = State.OFFLINE
        else:
            try:
                self.value = json.loads(self.data).get('state', self.UNKNOWN)
            except ValueError:
                self.value = self.UNKNOWN
            if self.value != State.FAILURE:
                # check if CRASHED
                timeout_expire = timezone.now()-settings.STATE_NODE_PULL_TIMEOUT
                if self.add_date < timeout_expire:
                    if not self.last_contact_on or self.last_contact_on < timeout_expire:
                        self.value = self.CRASHED
    
    def _store_soft_version(self):
            try:
                version = json.loads(self.data).get('soft_version')
            except ValueError:
                pass
            else:
                NodeSoftwareVersion.objects.store(self.content_object, version)
    
    def get_url(self):
        model = self.content_type.model_class()
        name = model.__name__.upper()
        URI = getattr(settings, "STATE_%s_%s" % (name, 'URI'))
        # If node doesn't have api use the default base uri
        node = self.get_node()
        base_uri = getattr(node.api, 'base_uri', NodeApi.default_base_uri(node))
        context = {
            'base_uri': base_uri,
            'object_id': self.object_id
        }
        return URI % context
    
    def get_current_display(self):
        current = self.current
        for name,verbose in State.STATES:
            if name == current:
                return verbose
        return current
    
    def get_node(self):
        return getattr(self.content_object, 'node', self.content_object)


class StateHistoryManager(models.Manager):
    def store(self, **kwargs):
        state = self.instance
        last_state = state.last
        now = timezone.now()
        if last_state:
            expiration = state.heartbeat_expires(last_state.end)
            if time() > expiration:
                last_state.end = datetime.fromtimestamp(expiration)
                last_state.save()
                last_state = state.history.create(start=last_state.end, end=now,
                        value=State.NODATA)
            else:
                last_state.end = now
                last_state.save()
        if not last_state or last_state.value != state.value:
            last_state = state.history.create(value=state.value, start=now, end=now,
                    data=state.data, metadata=state.metadata)
        return last_state


class StateHistory(models.Model):
    state = models.ForeignKey(State, related_name='history')
    value = models.CharField(max_length=32, choices=State.STATES)
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField()
    data = models.TextField(blank=True, default='')
    metadata = models.TextField(blank=True, default='')
    
    objects = StateHistoryManager()

    class Meta:
        ordering = ('-start',)
    
    def __unicode__(self):
        return self.value


class NodeSoftwareVersionManager(models.Manager):
    def store(self, node, version):
        if version:
            soft_version, __ = self.get_or_create(node=node)
            if soft_version.value != version:
                soft_version.value = version
                soft_version.save()
    
    def ordered_versions(self, branch=None):
        versions = self.distinct('value')
        if branch is not None:
            versions = [v for v in versions if v.version['branch'] == branch]
        return sorted(versions, key=lambda v: v.version['date'], reverse=True)


class NodeSoftwareVersion(models.Model):
    node = models.OneToOneField('nodes.Node', related_name='soft_version')
    value = models.CharField(max_length=256)
    
    objects = NodeSoftwareVersionManager()
    
    def __unicode__(self):
        return self.value
    
    @cached_property
    def version(self):
        """Return structured version data."""
        return extract_node_software_version(self.value)
    
    @cached_property
    def name(self):
        name = settings.STATE_NODE_SOFT_VERSION_NAME(self.version)
        return "%s (%s)" % (name, self.version['date'])
    
    @cached_property
    def url(self):
        return settings.STATE_NODE_SOFT_VERSION_URL(self.version)


node_heartbeat = Signal(providing_args=["instance", "node"])


@property
def state(self):
    ct = ContentType.objects.get_for_model(type(self))
    return self.state_set.get_or_create(object_id=self.id, content_type=ct)[0]

for model in [Node, Sliver]:
    model.add_to_class('state_set', generic.GenericRelation('state.State'))
    model.state = state
