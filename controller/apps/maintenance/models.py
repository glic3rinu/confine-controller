from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_transaction_signals import defer

from controller.utils import is_installed
from nodes.models import Node
from state.models import NodeState, node_heartbeat

from . import settings
from .exceptions import ConcurrencyError
from .tasks import run_instance


class Operation(models.Model):
    """ Defines an operation to be executed over a subset of nodes """
    name = models.CharField(max_length=256, help_text='Verbose name')
    identifier = models.CharField(max_length=16, help_text='Identifier used on the '
        'command line')
    script = models.TextField(help_text='Script to be executed on the nodes. Write '
        'it with atomicity in mind, there is no waranty that the script ends '
        'executed multiple times.')
    
    def __unicode__(self):
        return self.identifier
    
    def execute(self, nodes, include_new_nodes=False):
        instances = Execution.create(self, nodes, include_new_nodes)
        return instances


class Execution(models.Model):
    """
    Defines an execution of an operation, freezing its script definition and
    providing additional options
    """
    PROGRESS = 'PROGRESS'
    COMPLETE = 'COMPLETE'
    STATES = (
        (PROGRESS, PROGRESS),
        (COMPLETE, COMPLETE))
    
    operation = models.ForeignKey(Operation, related_name='executions')
    created_on = models.DateTimeField(auto_now_add=True)
    script = models.TextField()
    is_active = models.BooleanField(default=True)
    include_new_nodes = models.BooleanField()
    
    class Meta:
        ordering = ['-created_on']
    
    def __unicode__(self):
        return self.operation.identifier
    
    def revoke(self):
        for instance in self.instances:
            instance.revoke()
    
    @property
    def state(self):
        progress = [Instance.RECEIVED, Instance.STARTED, Instance.TIMEOUT]
        if self.instances.filter(state__in=progress).exists():
            return self.PROGRESS
        return self.COMPLETE
    
    @classmethod
    def create(cls, operation, nodes, include_new_nodes):
        cls.objects.filter(operation=operation,
            include_new_nodes=include_new_nodes).update(include_new_nodes=False)
        execution = cls.objects.create(operation=operation, script=operation.script,
            include_new_nodes=include_new_nodes)
        instances = []
        for node in nodes:
            instance = Instance.create(execution=execution, node=node)
            instance.run()
            instances.append(instance)
        return instances


@receiver(post_save, sender=Node)
def execute_on_new_nodes(sender, instance, signal, *args, **kwargs):
    """ creates needed execution instances when a new node is added """
    for execution in Execution.objects.filter(is_active=True, include_new_nodes=True):
        new_instance, new = Instance.objects.get_or_create(execution=execution, node=instance)
        if new:
            new_instance.run()


class Instance(models.Model):
    """ defines an operation execution in a particular node, keeping its state """
    RECEIVED = 'RECEIVED'
    TIMEOUT = 'TIMEOUT'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    REVOKED = 'REVOKED'
    OUTDATED = 'OUTDATED'
    
    STATES = (
        (RECEIVED, RECEIVED),
        (TIMEOUT, TIMEOUT),
        (STARTED, STARTED),
        (SUCCESS, SUCCESS),
        (FAILURE, FAILURE),
        (REVOKED, REVOKED),
        (OUTDATED, OUTDATED))
    
    execution = models.ForeignKey(Execution, related_name='instances')
    node = models.ForeignKey('nodes.Node', related_name='operations')
    state = models.CharField(max_length=16, choices=STATES, default=RECEIVED)
    last_try = models.DateTimeField(null=True)
    stdout = models.TextField()
    stderr = models.TextField()
    traceback = models.TextField()
    exit_code = models.IntegerField(null=True)
    
    def __unicode__(self):
        return "%s@%s" % (self.execution.operation.identifier, self.node)
    
    @classmethod
    def create(cls, execution, node):
        # outdate pending instances
        cls.objects.filter(execution__operation=execution.operation, node=node,
            state=cls.TIMEOUT).update(state=Instance.OUTDATED)
        instance = cls.objects.create(execution=execution, node=node)
        return instance
    
    def run(self, async=True):
        if self.state == self.STARTED:
            raise ConcurrencyError("One run at a time.")
        if async:
            defer(run_instance.delay, self.pk)
        else:
            run_instance(self.pk)
    
    def revoke(self):
        self.state = self.REVOKED
        self.save()
    
    @property
    def script(self):
        return self.execution.script


@receiver(node_heartbeat, sender=NodeState, dispatch_uid="maintenance.retry_pending_operations")
def retry_pending_operations(sender, node, **kwargs):
    """ runs timeout instances when a node heart beat is received """
    instances = Instance.objects.filter(node=node, state=Instance.TIMEOUT,
        execution__is_active=True)
    for instance in instances:
        instance.run()


if is_installed('firmware'):
    from firmware.models import construct_safe_locals
    @receiver(construct_safe_locals, dispatch_uid="maintenance.update_safe_locals")
    def update_safe_locals(sender, safe_locals, **kwargs):
        safe_locals.update(dict((setting, getattr(settings, setting))
            for setting in dir(settings) if setting.isupper() ))
