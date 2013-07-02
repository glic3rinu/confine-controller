from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from controller.utils.plugins import PluginModel


class Notification(PluginModel):
    message = models.TextField()
    
    def process(self):
        instance = self.instance
        for obj in instance.model.objects.all():
            valid_delivereds = self.delivered.filter(object_id=obj.pk, is_valid=True)
            if instance.check_condition(obj):
                if not valid_delivereds.exists():
                    self.deliver(obj)
            else:
                valid_delivereds.update(is_valid=False)
    
    def deliver(self, obj):
        recipients = self.instance.get_recipients(obj)
        send_email_template(self.message, recipients)
        self.delivered.create(content_object=obj)


class Delivered(models.Model):
    notification = models.ForeignKey(Notification, related_name='delivered')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True, help_text='Indicates whether the '
        'notification is still valid. Used in order to avoid repeated notifications '
        'when the condition is still valid')
    
    content_object = generic.GenericForeignKey()
