from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver, Signal

from controller.models.utils import generate_chainer_manager
from controller.utils import send_email_template

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
        if self.default:
            Queue.objects.filter(default=True).update(default=False)
        elif not Queue.objects.count():
            self.default = True
        super(Queue, self).save(*args, **kwargs)


class TicketQuerySet(models.query.QuerySet):
    def resolve(self, site):
        result = self.update(state=Ticket.RESOLVED)
        self.notify_users(site)
        return result
    
    def open(self, site):
        result = self.update(state=Ticket.OPEN)
        self.notify_users(site)
        return result
        
    def reject(self, site):
        result = self.update(state=Ticket.REJECTED)
        self.notify_users(site)
        return result
    
    def take(self, owner):
        return self.update(owner=owner)

    def notify_users(self, site):
        for ticket in self.all():
            ticket.notify_users(site)

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
    INTERNAL = 'INTERNAL'
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'
    VISIBILITY_CHOICES = ((INTERNAL, "Internal"),
                          (PUBLIC,  "Public"),
                          (PRIVATE, "Private"),)
    
    created_by = models.ForeignKey(get_user_model(), related_name='created_tickets')
    owner = models.ForeignKey(get_user_model(), null=True, blank=True,
        related_name='owned_tickets', verbose_name="Assigned to")
    queue = models.ForeignKey(Queue, related_name='tickets')
    subject = models.CharField(max_length=256)
    description = models.TextField()
    visibility = models.CharField(max_length=32, choices=VISIBILITY_CHOICES,
        default=PUBLIC, help_text="Internal: for the testbed operation staff<br/>\
                                   Public: for all RG researchers<br/>\
                                   Private: between user and staff")
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
    
    def notify_users(self, site, creator=True, owner=True, contrib=False):
        """ Send an email to ticket stakeholders notifying an state update """
        emails = []
        if creator:
            emails.append(self.created_by.email)
        if owner and self.owner:
            emails.append(self.owner.email)
        if contrib:
            for val in self.messages.distinct('author').values('author__email'):
                emails.append(val.get('author__email'))

        emails = list(set(emails + self.cc_emails)) #avoid duplicates
        template = 'issues/ticket_update_notification.mail'
        context = {'ticket': self, 'site': site}
        send_email_template(template, context, emails)

    def save(self, *args, **kwargs):
        # only set to open when an staff operator has repliyed or has owner
        has_replied_operator = self.messages.filter(author__is_superuser=True).exists()
        if self.state == self.NEW and (has_replied_operator or self.owner):
            self.state = self.OPEN

        new_issue = (not self.pk) # keep if is a new issue
        super(Ticket, self).save(*args, **kwargs)

        # notify operators if is a new issue
        if new_issue:
            to = settings.ISSUES_OPERATORS_EMAIL
            template = 'issues/ticket_new_notification.mail'
            context = {'ticket': self}
            send_email_template(template, context, to)
    
    @property
    def cc_emails(self):
        return self.cc.split(',') if self.cc else []

    def mark_as_read(self, user, is_read=True):
        tracker = self.tracker(user)
        if tracker is None:
            if is_read:
                return #do nothing cause is not tracked
            else: # create manual tracker
                tracker = self.tracker(user, create=True)
        tracker.is_read = is_read

    def is_read(self, user):
        tracker = self.tracker(user)
        if tracker is None:
            return True
        return tracker.is_read
    
    def tracker(self, user, create=False):
        try:
            tracker = self.trackers.get(user=user.id)
        except Tracker.DoesNotExist:
            if create:
                tracker = Tracker.objects.create(ticket=self, user=user, 
                                                 autogenerated=False)
            else:
                tracker = None #not tracked
        return tracker
        

class Message(models.Model):
    ticket = models.ForeignKey('issues.Ticket', related_name='messages')
    author = models.ForeignKey(get_user_model())
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return str(self.id)


class Tracker(models.Model):
    READ = 'READ'
    UNREAD = 'UNREAD'
    STATES= ((READ, "Read"),
             (UNREAD, "Unread"),)

    ticket = models.ForeignKey('issues.Ticket', related_name='trackers')
    user = models.ForeignKey(get_user_model())
    state = models.CharField(max_length=32, choices=STATES, default=UNREAD)
    autogenerated = models.BooleanField(default=True)

    class Meta:
        unique_together = ('ticket', 'user')

    def __unicode__(self):
        return "t%s_%s_%s" % (str(self.ticket), str(self.user), self.state)

    @property
    def is_read(self):
        return self.state == Tracker.READ

    @is_read.setter
    def is_read(self, value):
        if value:
            self.state = Tracker.READ
        else:
            self.state = Tracker.UNREAD
        self.save() # write change to DB

# custom signal for ticket_save hooking user
ticket_save = Signal(providing_args=["sender", "instance", "created", "user"])

@receiver(ticket_save, sender=Ticket)    
def ticket_tracker(sender, instance, created, user, **kwargs):
    """ create or update the tickets trackers and purge the old """
    tr_author_state = tr_owner_state = Tracker.UNREAD
    # the user who updates the ticket has read alreday the ticket
    if user == instance.created_by:
        tr_author_state = Tracker.READ
    elif user == instance.owner:
        tr_owner_state = Tracker.READ
    
    data = [
        {'user': instance.created_by, 'state': tr_author_state },
        {'user': instance.owner, 'state': tr_owner_state},
    ]
    # create or update the trackers
    uids = []
    for tracker in data:
        if tracker['user'] is None:
           continue 
        tr, new = Tracker.objects.get_or_create(ticket=instance, 
                    user=tracker['user'])
        tr.state = tracker['state']
        tr.save()
        uids.append(tracker['user'].id)

    # remove old trackers (e.g. old ticket owner)
    Tracker.objects.filter(ticket=instance.id, autogenerated=True)\
                    .exclude(user__in=uids).delete()
