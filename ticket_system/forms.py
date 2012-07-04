from django import forms

from ticket_system import models

class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        exclude = ('creator', 'owner', 'status', 'creation_date', 'last_modification_date')

class MessageForm(forms.ModelForm):
    class Meta:
        model = models.Message
        exclude = ('ticket', 'author',)
