from common.models import generate_chainer_manager
from django.db import models


class QueueQuerySet(models.query.QuerySet):
    def get_default(self):
        return self.get(default=True)


class Queue(models.Model):
    name = models.CharField(max_length=128, unique=True)
    default = models.BooleanField(default=False)
    
    objects = generate_chainer_manager(QueueQuerySet)
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.default:
            Queue.objects.filter(default=True).update(default=False)
        elif not Queue.objects.count():
            self.default = True
        super(Queue, self).save(*args, **kwargs)


class TicketQuerySet(models.query.QuerySet):
    def resolve(self):
        return self.update(state=Ticket.RESOLVED)
    
    def open(self):
        return self.update(state=Ticket.OPEN)
        
    def reject(self):
        return self.update(state=Ticket.REJECTED)
    
    def take(self, owner):
        return self.update(owner=owner)


class Ticket(models.Model):
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    PRIORITIES = ((HIGH, "High"),
                  (MEDIUM, "Medium"),
                  (LOW, "Low"),)
    NEW = 'NEW'
    OPEN = 'OPEN'
    RESOLVED = 'RESOLVED'
    REJECTED = 'REJECTED'
    STATES = ((NEW, "New"),
              (OPEN, "Open"),
              (RESOLVED, "Resolved"),
              (REJECTED, "Rejected"),)
    
    created_by = models.ForeignKey('auth.User')
    owner = models.ForeignKey('auth.User', null=True, blank=True,
        related_name='owned_tickets_set')
    queue = models.ForeignKey(Queue)
    subject = models.CharField(max_length=256)
    priority = models.CharField(max_length=32, choices=PRIORITIES, default=MEDIUM)
    state = models.CharField(max_length=32, choices=STATES, default=NEW)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified_on = models.DateTimeField(auto_now=True)
    cc = models.TextField('CC', blank=True)
    
    objects = generate_chainer_manager(TicketQuerySet)
    
    class Meta:
        ordering = ["-last_modified_on"]
    
    def __unicode__(self):
        return str(self.id)
    
    def save(self, *args, **kwargs):
        # FIXME only set to open when an staff operator has replyed
        if self.state == self.NEW and self.message_set.all().count() > 1:
            self.state = self.OPEN
        super(Ticket, self).save(*args, **kwargs)


class Message(models.Model):
    INTERNAL = 'INTERNAL'
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'
    VISIBILITY_CHOICES = ((INTERNAL, "Internal"),
                          (PUBLIC,  "Public"),
                          (PRIVATE, "Private"),)
    
    ticket = models.ForeignKey('issues.Ticket')
    author = models.ForeignKey('auth.User')
    visibility = models.CharField(max_length=32, choices=VISIBILITY_CHOICES, 
        default=PUBLIC)
    content = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return str(self.id)


