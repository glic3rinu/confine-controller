from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Queue(models.Model):
    name = models.CharField(max_length=128, unique=True)
    
    def __unicode__(self):
        return self.name


class Ticket(models.Model):

    PRIORITIES = (('high', _("High")),
                  ('hedium', _("Medium")),
                  ('low', _("Low")),)

    STATES = (('new', _("New")),
              ('open', _("Open")),
              ('resolved', _("Resolved")),
              ('rejected', _("Rejected")),)

    created_by = models.ForeignKey(User)
    owner = models.ForeignKey(User, related_name='ticket_owned_set', null=True, blank=True)
    queue = models.ForeignKey(Queue)
    subject = models.CharField(max_length=256)
    priority = models.CharField(max_length=32, choices=PRIORITIES, default='medium')
    state = models.CharField(max_length=32, choices=STATES, default='new')
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified_on = models.DateTimeField(auto_now=True)
    cc = models.TextField(blank=True, verbose_name="CC")

    class Meta:
        ordering = ["-last_modified_on"]

    def __unicode__(self):
        return str(self.id)


class Message(models.Model):

    VISIBILITY_CHOICES = (('internal', _("Internal")),
                          ('public', _("Public")),
                          ('private', _("Private")),)

    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(User)
    visibility = models.CharField(max_length=32, choices=VISIBILITY_CHOICES, default='public')
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name
