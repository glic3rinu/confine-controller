from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


def get_conditions():
    return ('', '')


class Notification(models.Model):
    condition = models.IntegerField(choices=get_conditions)
    model = models.ForeignKey(ContentType)
    queryset = models.CharField(max_length=256, blank=True, help_text="queryset.filter(id=233)")
    recipient = models.CharField(max_lenght=256)
    message = models.TextField()
    is_active = models.BooleanField()
    
    def check(self):
        model = self.model.model_class()
        queryset = model.objects.all()
        if self.queryset:
            queryset = eval(self.queryset, {'queryset':queryset})
        for obj in queryset:
            if eval(condition, {'obj': obj}):
                if not self.delivered.filter(object_id=obj.pk, is_valid=True).exists():
                    self.deliver(obj)
            else:
                self.delivered.filter(object_id=obj.pk, is_valid=True).update(is_valid=False)
    
    def deliver(self, obj):
        recipient = eval(recipient, {'obj': obj})
        send_email_template(self.message, recipient)
        self.delivered.create(content_object=obj)


class Delivered(models.Model):
    notification = models.ForeignKey(Notification, related_name='delivered')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    
    content_object = generic.GenericForeignKey()
