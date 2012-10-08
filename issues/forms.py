from common.forms import colored_field, admin_link
from common.widgets import ShowText
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


class MessageInlineForm(forms.ModelForm):
    author = forms.CharField(label="Author", widget=ShowText(bold=True), required=False)
    created_on = forms.CharField(label="Created On", widget=ShowText(), required=False)

    class Meta:
        fields = ('content', 'visibility',)

    def __init__(self, *args, **kwargs):
        try: self.user = kwargs.pop('user')
        except KeyError: pass
        super(MessageInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.initial['author'] = admin_link(instance.author)
            self.initial['created_on'] = instance.created_on.strftime("%Y-%m-%d %H:%M:%S")
            self.fields['content'].widget = ShowText()
        else: 
            self.initial['author'] = ''
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


