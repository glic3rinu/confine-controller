from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
from jsonfield import JSONField

from slices.models import Sliver

from .helpers import extract_sliver_data


class SliverLog(models.Model):
    slice = models.ForeignKey('slices.Slice', null=True, related_name='+',
            on_delete=models.SET_NULL)
    node = models.ForeignKey('nodes.Node', null=True, related_name='+')
    created_on = models.DateField(auto_now_add=True,
            help_text='Date when the sliver is registered for first time.')
    expires_on = models.DateField(null=True,
            help_text='Date when the sliver expires (or it has expired).')
    data = JSONField(help_text='Log info: experiment/service description, '
                                'about the owner group...')
    
    @property
    def description(self):
        try:
            sliver = Sliver.objects.get(node=self.node, slice=self.slice)
        except Sliver.DoesNotExist:
            return self.data['description']
        else:
            return sliver.description
    
    @property
    def group(self):
        if self.slice is None:
            return self.data['group']
        return self.slice.group
    
    @property
    def slice_data(self):
        #TODO(santiago): handle in a transparent way slice & slice_data
        if self.slice is None:
            return self.data['slice']
        return self.slice


## SIGNALS ##
def log_sliver_event(instance, event):
    """Create or update sliver log."""
    log, _ = SliverLog.objects.get_or_create(slice=instance.slice, node=instance.node)
    log.data = extract_sliver_data(instance)
    log.expires_on = instance.slice.expires_on if event == 'create' else now()
    log.save()


@receiver(post_save, sender=Sliver)
def log_sliver_deployment(sender, instance, raw, **kwargs):
    if raw:
        return
    log_sliver_event(instance, event='create')


@receiver(pre_delete, sender=Sliver)
def log_sliver_expiration(sender, instance, **kwargs):
    log_sliver_event(instance, event='delete')
