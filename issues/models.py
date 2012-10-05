from common.models import generate_chainer_manager
from django.contrib.auth.models import User
from django.db import models


class Queue(models.Model):
    name = models.CharField(max_length=128, unique=True)
    default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.default:
            Queue.objects.filter(default=True).update(default=False)
        super(Queue, self).save(*args, **kwargs)


class TicketQuerySet(models.query.QuerySet):
    def resolve(self):
        return self.update(state='RESOLVED')

    def open(self):
        return self.update(state='OPEN')
        
    def reject(self):
        return self.update(state='REJECTED')

    def take(self, owner):
        return self.update(owner=owner)


class Ticket(models.Model):
    PRIORITIES = (('HIGH', "High"),
                  ('MEDIUM', "Medium"),
                  ('LOW', "Low"),)

    STATES = (('NEW', "New"),
              ('OPEN', "Open"),
              ('RESOLVED', "Resolved"),
              ('REJECTED', "Rejected"),)

    created_by = models.ForeignKey(User)
    owner = models.ForeignKey(User, related_name='ticket_owned_set', null=True, blank=True)
    queue = models.ForeignKey(Queue)
    subject = models.CharField(max_length=256)
    priority = models.CharField(max_length=32, choices=PRIORITIES, default='MEDIUM')
    state = models.CharField(max_length=32, choices=STATES, default='NEW')
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified_on = models.DateTimeField(auto_now=True)
    cc = models.TextField(blank=True, verbose_name="CC")

    objects = generate_chainer_manager(TicketQuerySet)

    class Meta:
        ordering = ["-last_modified_on"]

    def __unicode__(self):
        return str(self.id)


class Message(models.Model):
    VISIBILITY_CHOICES = (('INTERNAL', "Internal"),
                          ('PUBLIC',  "Public"),
                          ('PRIVATE', "Private"),)

    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(User)
    visibility = models.CharField(max_length=32, choices=VISIBILITY_CHOICES, default='PUBLIC')
    content = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.id)
