from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_transaction_signals import defer

from nodes.models import Node
from state.models import NodeState, node_heartbeat

from .tasks import run_instance


class Operation(models.Model):
    name = models.CharField(max_length=256, help_text='Verbose name')
    identifier = models.CharField(max_length=16, help_text='Identifier used on the '
        'command line')
    script = models.TextField()
    
    def __unicode__(self):
        return self.identifier
    
    def execute(self, nodes, include_new_nodes=False):
        for execution in Execution.objects.filter(operation=self, is_active=True):
            execution.is_active = False
            execution.save()
        execution = Execution.objects.create(operation=self, script=self.script,
            include_new_nodes=include_new_nodes)
        for node in nodes:
            instance = Instance.objects.create(execution=execution, node=node)
            instance.run()


class Execution(models.Model):
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
        for instance in Instance.objects.filter(execution=self):
            instance.revoke()


@receiver(post_save, sender=Node)
def execute_on_new_nodes(sender, instance, signal, *args, **kwargs):
    """ Make sure to create needed execution instances when a new node is added """
    for execution in Execution.objects.filter(is_active=True, include_new_nodes=True):
        instance, new = Instance.objects.get_or_create(execution=execution, node=instance)


class Instance(models.Model):
    RECEIVED = 'RECEIVED'
    TIMEOUT = 'TIMEOUT'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    REVOKED = 'REVOKED'
    
    STATES = (
        (RECEIVED, RECEIVED),
        (TIMEOUT, TIMEOUT),
        (STARTED, STARTED),
        (SUCCESS, SUCCESS),
        (FAILURE, FAILURE),
        (REVOKED, REVOKED))
    
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
    
    def run(self, async=True):
        if self.state == self.STARTED:
            raise self.ConcurrencyError("One run at a time.")
        if async:
            defer(run_instance.delay, self.pk)
        else:
            run_instance(self.pk)
    
    def revoke(self):
        self.state = self.REVOKED
    
    class ConcurrencyError(Exception): pass


@receiver(node_heartbeat, sender=NodeState)
def retry_pending_operations(sender, node, **kwargs):
    instances = Instance.objects.filter(node=node, state=Instance.TIMEOUT,
        execution__is_active=True)
    for instance in instances:
        instance.run()
