from django.db import models
from django.contrib.auth import models as auth_models

import datetime

PRIORITY_CHOICES = (
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low')
    )

STATUS_CHOICES = (
    ('New', 'New'),
    ('Open', 'Open'),
    ('Resolved', 'Resolved'),
    ('Rejected', 'Rejected')
    )

class Ticket(models.Model):
    # Relations
    creator = models.ForeignKey(auth_models.User,
                                verbose_name = "creator",
                                related_name = "created_ticket"
                                )
    owner = models.ForeignKey(auth_models.User,
                              blank = True,
                              null = True,
                              verbose_name = "owner",
                              related_name = "pending_ticket")
    queue = models.ForeignKey("Queue",
                              verbose_name = "queue")

    # Attributes
    subject = models.CharField(max_length = 200,
                               verbose_name = "subject")
    content = models.TextField(verbose_name = "content")
    priority = models.CharField(max_length = 50,
                                choices = PRIORITY_CHOICES)
    status = models.CharField(max_length = 50,
                              choices = STATUS_CHOICES)
    creation_date = models.DateTimeField(verbose_name = "creation date")
    last_modification_date = models.DateTimeField(verbose_name = "last modification date")
    cc_mails = models.TextField(verbose_name = "CC Mails",
                                null = True,
                                blank = True)
   
    
    # Functions
    def __unicode__(self):
        return "%s" % self.subject

    def save(self, *args, **kwargs):
        self.last_modification_date = datetime.datetime.now()
        super(Ticket, self).save(*args, **kwargs)

    def get_fields(self):
        return map(lambda a: [a.name, getattr(self, a.name)], Ticket._meta.fields)
        
        
    class Meta:
        verbose_name = "ticket"
        verbose_name_plural = "tickets"
        ordering = ["-last_modification_date"]

class Queue(models.Model):
    # Relations

    # Attributes
    name = models.CharField(max_length = 200,
                               verbose_name = "name")
    
    # Functions
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name = "queue"
        verbose_name_plural = "queues"

VISIBILITY_CHOICES = (
    ('Internal', 'Internal'),
    ('Public', 'Public'),
    ('Private', 'Private')
    )

class Message(models.Model):
    # Relations
    ticket = models.ForeignKey("Ticket",
                              verbose_name = "ticket")
    author = models.ForeignKey(auth_models.User,
                               verbose_name = "author",
                               related_name = "ticket_messages"
                               )

    # Attributes
    visibility = models.CharField(max_length = 200,
                                  choices = VISIBILITY_CHOICES,
                                  verbose_name = "visibility")
    content = models.TextField(verbose_name = "content")
    
    # Functions
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name = "queue"
        verbose_name_plural = "queues"

