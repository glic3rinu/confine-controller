from django.db import models, connection
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.template import Context, Template
from django.utils import timezone

from controller.utils.plugins.models import PluginModel


class Notification(PluginModel):
    subject = models.CharField(max_length=256)
    message = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.hook_delivered_generic_relation()
        super(Notification, self).save(*args, **kwargs)
    
    def process(self):
        instance = self.instance
        for obj in instance.model.objects.all():
            valid_delivereds = self.delivered.filter(object_id=obj.pk, is_valid=True)
            # purge expired delivered instances
            if instance.expire_window is not None:
                expiration_time = timezone.now() - instance.expire_window
                valid_delivereds.filter(date__lt=expiration_time).delete()
            
            if instance.check_condition(obj):
                if not valid_delivereds.exists():
                    self.deliver(obj)
            else:
                valid_delivereds.update(is_valid=False)
    
    def deliver(self, obj):
        email_from = None
        email_to = self.instance.get_recipients(obj)
        context = Context(self.instance.get_context(obj))
        raw_subject = self.subject or self.instance.default_subject
        raw_message = self.message or self.instance.default_message
        subject = Template(raw_subject).render(context)
        message = Template(raw_message).render(context)
        send_mail(subject, message, email_from, email_to)
        self.delivered.create(content_object=obj)
    
    def hook_delivered_generic_relation(self):
        model = self.instance.model
        for field in model._meta.local_many_to_many:
            if field.rel.to == Delivered:
                return
        relation = generic.GenericRelation('notifications.Delivered')
        model.add_to_class('notifications', relation)


class Delivered(models.Model):
    notification = models.ForeignKey(Notification, related_name='delivered')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True,
            help_text='Indicates whether the notification is still valid. Used in order '
                      'to avoid repeated notifications when the condition is still valid')
    
    content_object = generic.GenericForeignKey()
    
    def __unicode__(self):
        return unicode(self.content_object)


try:
    # This may fail when the database does not exists
    cursor = connection.cursor()
except:
    pass
else:
    if Notification._meta.db_table in connection.introspection.get_table_list(cursor):
        for notification in Notification.objects.all():
            try:
                instance = notification.instance
            except AttributeError:
                # Catch and purge notification that exists in DB
                # but not in code (doesn't have plugin)
                notification.delete()
            else:
                notification.hook_delivered_generic_relation()
