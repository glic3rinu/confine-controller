from django import forms
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from controller.forms.utils import admin_link
from controller.forms.widgets import ShowText

from issues.models import Queue, Ticket
from issues.helpers import format_date


class MarkDownWidget(forms.Textarea):
    """ MarkDown textarea widget with syntax preview """
    def render(self, name, value, attrs):
        url = '/static/issues/markdown_syntax.html'
        help_link = '<a href="%s" onclick=\'window.open("%s", "", "resizable=yes, \
            location=no, width=300, height=640, menubar=no, status=no, \
            scrollbars=yes"); return false;\'>markdown format</a>' % (url, url)
        textarea = super(MarkDownWidget, self).render(name, value, attrs)
        preview = '<a id="load-preview" href="#">preview</a>\
                   <div id="content-preview"></div>'
        return mark_safe("<p class='help'>HTML not allowed, you can use \
                          %s<br/>%s<br/>%s</p>" % (help_link, textarea, preview))


class MessageInlineForm(forms.ModelForm):
    """  Add message form """
    author_link = forms.CharField(label="Author", widget=ShowText(bold=True), required=False)
    created_on = forms.CharField(label="Created On", widget=ShowText(), required=False)
    content = forms.CharField(widget=MarkDownWidget(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(MessageInlineForm, self).__init__(*args, **kwargs)
        self.initial['author_link'] = '</b>'+admin_link(self.user)
        self.initial['created_on'] = ''

#    def clean_content(self):
#        """  clean HTML tags """
#        return strip_tags(self.cleaned_data['content'])
    
    def save(self, *args, **kwargs):
        if self.instance.pk is None:
            self.instance.author = self.user
        return super(MessageInlineForm, self).save(*args, **kwargs)


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

