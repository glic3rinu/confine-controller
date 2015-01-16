from django import forms
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from markdown import markdown

from controller.forms.utils import admin_link
from controller.forms.widgets import ReadOnlyWidget, ShowText
from users.models import User

from .models import Queue, Ticket


markdown_url = '/static/issues/markdown_syntax.html'
markdown_help_text = ('<a href="%s" onclick=\'window.open("%s", "", "resizable=yes,'
    'location=no, width=300, height=640, menubar=no, status=no, scrollbars=yes"); '
    'return false;\'>markdown format</a>' % (markdown_url, markdown_url))
markdown_help_text = 'HTML not allowed, you can use %s' % markdown_help_text


class MarkDownWidget(forms.Textarea):
    """ MarkDown textarea widget with syntax preview """
    def render(self, name, value, attrs):
        widget_id = attrs['id'] if attrs and 'id' in attrs else 'id_%s' % name
        textarea = super(MarkDownWidget, self).render(name, value, attrs)
        preview = ('<a class="load-preview" href="#" data-field="{0}">preview</a>'\
                   '<div id="{0}-preview" class="content-preview"></div>'.format(widget_id))
        return mark_safe('<p class="help">%s<br/>%s<br/>%s</p>' % (
            markdown_help_text, textarea, preview))


class MessageInlineForm(forms.ModelForm):
    """  Add message form """
    author_link = forms.CharField(label="Author", widget=ShowText(bold=True), required=False)
    created_on = forms.CharField(label="Created On", widget=ShowText(), required=False)
    content = forms.CharField(widget=MarkDownWidget(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(MessageInlineForm, self).__init__(*args, **kwargs)
        self.initial['author_link'] = '</b>'+admin_link(self.user)
        self.initial['created_on'] = ''
    
    def clean_content(self):
        """  clean HTML tags """
        return strip_tags(self.cleaned_data['content'])
    
    def save(self, *args, **kwargs):
        if self.instance.pk is None:
            self.instance.author = self.user
        return super(MessageInlineForm, self).save(*args, **kwargs)


class UsersIterator(forms.models.ModelChoiceIterator):
    """ Group ticket owner by superusers, ticket.group and regular users """
    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop('ticket', False)
        super(forms.models.ModelChoiceIterator, self).__init__(*args, **kwargs)

    def __iter__(self):
        yield ('', '---------')
        users = User.objects.exclude(is_active=False).order_by('name')
        superusers = users.filter(is_superuser=True)
        if superusers:
            yield ('Operators', list(superusers.values_list('pk', 'name')))
            users = users.exclude(is_superuser=True)
        if self.ticket and self.ticket.group:
            group = users.filter(groups=self.ticket.group)
            if group:
                yield ('Group', list(group.values_list('pk', 'name')))
                users = users.exclude(groups=self.ticket.group)
        if users:
            yield ('Other', list(users.values_list('pk', 'name')))


class TicketForm(forms.ModelForm):
    display_description = forms.CharField(label="Description", required=False)
    description = forms.CharField(widget=MarkDownWidget(attrs={'class':'vLargeTextField'}))
    
    class Meta:
        model = Ticket
        exclude = ('last_modified_on', 'cc',)
    
    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        ticket = kwargs.get('instance', False)
        if not ticket:
            # Provide default ticket queue for new ticket
            try:
                self.initial['queue'] = Queue.objects.get_default().id
            except Queue.DoesNotExist:
                pass
            user_choices = UsersIterator()
        else:
            description = markdown(ticket.description)
            # some hacks for better line breaking
            description = description.replace('>\n', '#Ha9G9-?8')
            description = description.replace('\n', '<br>')
            description = description.replace('#Ha9G9-?8', '>\n')
            description = '<br><br>' + description
            widget = ReadOnlyWidget(description, description)
            self.fields['display_description'].widget = widget
            user_choices = UsersIterator(ticket=ticket)
        if 'owner' in self.fields:
            self.fields['owner'].choices = user_choices
    
    def clean_description(self):
        """  clean HTML tags """
        return strip_tags(self.cleaned_data['description'])


class ChangeReasonForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'cols': '100', 'rows': '10'}),
        required=False)
