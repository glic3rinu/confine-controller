from django.contrib.auth import get_user_model
from django.db import models

from controller.models.utils import generate_chainer_manager
from controller.utils import send_email_template
from users.models import Group

from issues import settings


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
        """ mark as default queue if needed """
        existing_default = Queue.objects.filter(default=True)
        if self.default:
            existing_default.update(default=False)
        elif not existing_default:
            self.default = True
        super(Queue, self).save(*args, **kwargs)


class TicketQuerySet(models.query.QuerySet):
    def progress(self):
        return self.update(state=Ticket.IN_PROGRESS)
    
    def resolve(self):
        return self.update(state=Ticket.RESOLVED)
    
    def feedback(self):
        return self.update(state=Ticket.FEEDBACK)
    
    def reject(self):
        return self.update(state=Ticket.REJECTED)
    
    def close(self):
        return self.update(state=Ticket.CLOSED)
    
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
    IN_PROGRESS = 'IN_PROGRESS'
    RESOLVED = 'RESOLVED'
    FEEDBACK = 'FEEDBACK'
    REJECTED = 'REJECTED'
    CLOSED = 'CLOSED'
    STATES = ((NEW, "New"),
              (IN_PROGRESS, "In Progress"),
              (RESOLVED, "Resolved"),
              (FEEDBACK, "Feedback"),
              (REJECTED, "Rejected"),
              (CLOSED, "Closed"),)
    INTERNAL = 'INTERNAL'
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'
    VISIBILITY_CHOICES = ((INTERNAL, "Internal"),
                          (PUBLIC,  "Public"),
                          (PRIVATE, "Private"),)
    
    created_by = models.ForeignKey(get_user_model(), related_name='created_tickets')
    group = models.ForeignKey(Group, null=True, blank=True, related_name='assigned_tickets')
    owner = models.ForeignKey(get_user_model(), null=True, blank=True,
        related_name='owned_tickets', verbose_name='assigned to')
    queue = models.ForeignKey(Queue, related_name='tickets')
    subject = models.CharField(max_length=256)
    description = models.TextField()
    visibility = models.CharField(max_length=32, choices=VISIBILITY_CHOICES, default=PUBLIC)
    priority = models.CharField(max_length=32, choices=PRIORITIES, default=MEDIUM)
    state = models.CharField(max_length=32, choices=STATES, default=NEW)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified_on = models.DateTimeField(auto_now=True)
    cc = models.TextField('CC', blank=True, help_text="emails to send a carbon copy")
    
    objects = generate_chainer_manager(TicketQuerySet)
    
    class Meta:
        ordering = ["-last_modified_on"]
    
    def __unicode__(self):
        return str(self.id)
    
    def notify(self, message=None, content=None):
        """ Send an email to ticket stakeholders notifying an state update """
        # TODO notify admin
        emails = [self.created_by.email]
        if self.owner:
            emails.append(self.owner.email)
        for val in self.messages.distinct('author').values('author__email'):
            emails.append(val.get('author__email'))
        
        emails = set(emails + self.cc_emails) # avoid duplicates
        template = 'issues/ticket_notification.mail'
        context = {
            'ticket': self,
            'ticket_message': message}
        send_email_template(template, context, emails)
    
    def save(self, *args, **kwargs):
        """ notify stakeholders of new ticket """
        new_issue = not self.pk
        super(Ticket, self).save(*args, **kwargs)
        if new_issue:
            self.notify()
    
    @property
    def cc_emails(self):
        return self.cc.split(',') if self.cc else []
    
    def mark_as_read_by(self, user):
        TicketTracker.objects.get_or_create(ticket=self, user=user)
    
    def mark_as_unread_by(self, user):
        ReadTicket.objects.filter(ticket=self, user=user).delete()
    
    def mark_as_unread(self):
        TicketTracker.objects.filter(ticket=self).delete()
    
    def is_read_by(self, user):
        return TicketTracker.objects.filter(ticket=self, user=user).exists()


class Message(models.Model):
    ticket = models.ForeignKey('issues.Ticket', related_name='messages')
    author = models.ForeignKey(get_user_model())
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        messages = self.ticket.messages.order_by('created_on').values_list('id', flat=True)
        return "#%s" % str(list(messages).index(self.id)+1)
    
    def save(self, *args, **kwargs):
        """ notify stakeholders of ticket update """
        if not self.pk:
            self.ticket.mark_as_unread()
            self.ticket.notify(message=self)
        super(Message, self).save(*args, **kwargs)


class TicketTracker(models.Model):
    """ Keeps track of user read tickets """
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(get_user_model())
    
    class Meta:
        unique_together = (('ticket', 'user'),)
