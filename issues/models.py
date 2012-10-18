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
    
    @property
    def num_tickets(self):
        return self.ticket_set.all().count()
    
    @property
    def num_messages(self):
        return Message.objects.filter(ticket__queue=self).count()


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
    
    created_by = models.ForeignKey('auth.User')
    owner = models.ForeignKey('auth.User', null=True, blank=True,
        related_name='owned_tickets_set')
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
    
    def save(self, *args, **kwargs):
        # FIXME only set to open when an staff operator has replyed
        if self.state == 'NEW' and self.num_messages > 1:
            self.state = 'OPEN'
        super(Ticket, self).save(*args, **kwargs)
    
    @property
    def num_messages(self):
        return self.message_set.all().count()


class Message(models.Model):
    VISIBILITY_CHOICES = (('INTERNAL', "Internal"),
                          ('PUBLIC',  "Public"),
                          ('PRIVATE', "Private"),)
    
    ticket = models.ForeignKey('issues.Ticket')
    author = models.ForeignKey('auth.User')
    visibility = models.CharField(max_length=32, choices=VISIBILITY_CHOICES, default='PUBLIC')
    content = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return str(self.id)


