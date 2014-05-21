from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from controller.models.utils import generate_chainer_manager
from controller.utils import send_email_template
from users.models import Group, Roles, User

from . import settings


class QueueQuerySet(models.query.QuerySet):
    def get_default(self):
        return self.get(default=True)


class Queue(models.Model):
    name = models.CharField(max_length=128, unique=True)
    default = models.BooleanField(default=False)
    notify_group_admins = models.BooleanField(default=True)
    notify_node_admins = models.BooleanField(default=False)
    notify_slice_admins = models.BooleanField(default=False)
    
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
    def involved_by(self, user, *args, **kwargs):
        qset = Q(created_by=user) | Q(owner=user)
        qset = qset | Q(messages__author=user) | Q(group__in=user.groups.all())
        return self.filter(qset, *args, **kwargs).distinct()
    
    def visible_by(self, user, *args, **kwargs):
        if user.is_superuser:
            return self.filter(*args, **kwargs)
        public = Q(visibility=Ticket.PUBLIC)
        private = Q(created_by=user) | Q(owner=user)
        private = private | Q(group__in=user.groups.all())
        private = Q(visibility=Ticket.PRIVATE) & Q(private)
        return self.filter(Q(public | private)).distinct().filter(*args, **kwargs)


class Ticket(models.Model):
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    PRIORITIES = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    RESOLVED = 'RESOLVED'
    FEEDBACK = 'FEEDBACK'
    REJECTED = 'REJECTED'
    CLOSED = 'CLOSED'
    STATES = (
        (NEW, 'New'),
        (IN_PROGRESS, 'In Progress'),
        (RESOLVED, 'Resolved'),
        (FEEDBACK, 'Feedback'),
        (REJECTED, 'Rejected'),
        (CLOSED, 'Closed'),
    )
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'
    VISIBILITY_CHOICES = (
        (PUBLIC,  'Public'),
        (PRIVATE, 'Private'),
    )
    
    created_by = models.ForeignKey(get_user_model(), null=True, blank=True,
            related_name='created_tickets', on_delete=models.SET_NULL)
    created_by_name = models.CharField(max_length=60)
    group = models.ForeignKey(Group, null=True, blank=True, related_name='assigned_tickets')
    owner = models.ForeignKey(get_user_model(), null=True, blank=True,
            related_name='owned_tickets', verbose_name='assigned to')
    queue = models.ForeignKey(Queue, related_name='tickets', null=True, blank=True)
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
        return unicode(self.pk)
    
    def get_notification_emails(self):
        """ Get emails of the users related to the ticket """
        emails = list(settings.ISSUES_SUPPORT_EMAILS)
        emails.append(self.created_by.email)
        if self.owner:
            emails.append(self.owner.email)
        else: # No ticket owner, so lets notify staff
            if settings.ISSUES_NOTIFY_SUPERUSERS:
                superusers = User.objects.filter(is_superuser=True)
                emails += superusers.values_list('email', flat=True)
            if self.group:
                roles = [Roles.GROUP_ADMIN]
                if self.queue: # check if other roles must be notified
                    if self.queue.notify_node_admins:
                        roles.append(Roles.NODE_ADMIN)
                    if self.queue.notify_slice_admins:
                        roles.append(Roles.SLICE_ADMIN)
                emails += self.group.get_emails(roles=roles)
        for message in self.messages.distinct('author'):
            author = message.author
            if self.is_visible_by(author):
                emails.append(author.email)
        return set(emails + self.cc_emails)
        
    def notify(self, message=None, content=None):
        """ Send an email to ticket stakeholders notifying an state update """
        emails = self.get_notification_emails()
        template = 'issues/ticket_notification.mail'
        html_template = 'issues/ticket_notification_html.mail'
        context = {
            'ticket': self,
            'ticket_message': message }
        send_email_template(template, context, emails, html=html_template)
    
    def save(self, *args, **kwargs):
        """ notify stakeholders of new ticket """
        new_issue = not self.pk
        super(Ticket, self).save(*args, **kwargs)
        if new_issue:
            # PK should be available for rendering the template
            self.notify()
    
    def is_involved_by(self, user):
        """ returns whether user has participated or is referenced on the ticket
            as owner or member of the group
        """
        return Ticket.objects.filter(pk=self.pk).involved_by(user).exists()
    
    def is_visible_by(self, user):
        """ returns whether ticket is visible by user """
        return Ticket.objects.filter(pk=self.pk).visible_by(user).exists()
    
    @property
    def cc_emails(self):
        return self.cc.split(',') if self.cc else []
    
    def mark_as_read_by(self, user):
        TicketTracker.objects.get_or_create(ticket=self, user=user)
    
    def mark_as_unread_by(self, user):
        TicketTracker.objects.filter(ticket=self, user=user).delete()
    
    def mark_as_unread(self):
        TicketTracker.objects.filter(ticket=self).delete()
    
    def is_read_by(self, user):
        return TicketTracker.objects.filter(ticket=self, user=user).exists()
    
    def reject(self):
        self.state = Ticket.REJECTED
        self.save()
    
    def resolve(self):
        self.state = Ticket.RESOLVED
        self.save()
    
    def close(self):
        self.state = Ticket.CLOSED
        self.save()
    
    def take(self, user):
        self.owner = user
        self.save()


class Message(models.Model):
    ticket = models.ForeignKey('issues.Ticket', related_name='messages')
    author = models.ForeignKey(get_user_model(), null=True, blank=True,
             on_delete=models.SET_NULL)
    author_name = models.CharField(max_length=60)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        num = self.ticket.messages.filter(id__lte=self.id).count()
        return u"#%i" % num
    
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


@receiver(pre_delete, sender=get_user_model())
def update_author_data(sender, instance, **kwargs):
    """save author info for using when user is deleted (#289)"""
    # update tickets
    for ticket in instance.created_tickets.all():
        ticket.created_by_name = ticket.created_by.name
        ticket.save()
    
    # update messages
    for msg in instance.message_set.all():
        msg.author_name = msg.author.name
        msg.save()
