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
            author_change = reverse('admin:auth_user_change', args=(instance.author.pk,))
            author_change = mark_safe("<a href='%s'>%s</a>" % (author_change, instance.author))
            self.initial['author'] = author_change
            self.initial['created_on'] = instance.created_on.strftime("%Y-%m-%d %H:%M:%S")
            self.fields['content'].widget = ShowText()
        else: 
            self.initial['author'] = ''
            self.initial['created_on'] = ''

    def save(self, *args, **kwargs):
        if self.instance.pk is None:
            self.instance.author = self.user
        return super(MessageInlineForm, self).save(*args, **kwargs)
