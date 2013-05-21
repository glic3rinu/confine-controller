from django import forms

from controller.forms.utils import colored_field, admin_link
from controller.forms.widgets import ShowText

from issues.models import Queue, Ticket
from issues.helpers import format_date

class MessageInlineForm(forms.ModelForm):
    author_link = forms.CharField(label="Author", widget=ShowText(bold=True), required=False)
    created_on = forms.CharField(label="Created On", widget=ShowText(), required=False)
    
    class Meta:
        fields = ('content',)
    
    def __init__(self, *args, **kwargs):
        super(MessageInlineForm, self).__init__(*args, **kwargs)
        message = kwargs.get('instance', False)
        if message:
            # Display message form
            self.initial['author_link'] = '</b>'+admin_link(message.author)
            self.initial['created_on'] = format_date(message.created_on)
            if 'content' in self.fields:
                # read only fields doesn't have content
                self.fields['content'].widget = ShowText()
                self.fields['content'].required = False
        else:
            # Add message form
            self.initial['author_link'] = '</b>'+admin_link(self.user)
            self.initial['created_on'] = ''
    
    def save(self, *args, **kwargs):
        if self.instance.pk is None:
            self.instance.author = self.user
        return super(MessageInlineForm, self).save(*args, **kwargs)


class TicketInlineForm(forms.ModelForm):
    ticket_id = forms.CharField(label="ID", widget=ShowText(bold=True), required=False)
    subject = forms.CharField(label="Subject", widget=ShowText(bold=True), required=False)
    created_by = forms.CharField(label="Created by", widget=ShowText(), required=False)
    owner = forms.CharField(label="Owner", widget=ShowText(), required=False)
    state = forms.CharField(label="State", widget=ShowText(bold=True), required=False)
    priority = forms.CharField(label="Priority", widget=ShowText(bold=True), required=False)
    created_on = forms.CharField(label="Created on", widget=ShowText(), required=False)
    last_modified_on = forms.CharField(label="Last modified on", widget=ShowText(), required=False)
    
    class Meta:
        fields = ()
    
    def __init__(self, *args, **kwargs):
        super(TicketInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            # Avoid circular imports
            from issues.admin import STATE_COLORS, PRIORITY_COLORS
            instance = kwargs['instance']
            self.initial['ticket_id'] = admin_link(instance)
            self.initial['subject'] = admin_link(instance, title=instance.subject)
            self.initial['created_by'] = admin_link(instance.created_by)
            self.initial['owner'] = admin_link(instance.owner) if instance.owner else ''
            self.initial['state'] = colored_field(instance.state, STATE_COLORS)
            self.initial['priority'] = colored_field(instance.priority, PRIORITY_COLORS)
            self.initial['created_on'] = instance.created_on.strftime("%Y-%m-%d %H:%M:%S")
            self.initial['last_modified_on'] = instance.last_modified_on.strftime("%Y-%m-%d %H:%M:%S")

class TicketForm(forms.ModelForm):
    queue = forms.ModelChoiceField(queryset = Queue.objects.all())

    class Meta:
        model = Ticket

    def __init__(self, *args, **kwargs):
        """ Provide default ticket queue for new tickets """
        super(TicketForm, self).__init__(*args, **kwargs)
        if not 'instance' in kwargs:
            try:
                self.initial['queue'] = Queue.objects.get_default().id
            except Queue.DoesNotExist:
                pass      

