from django import forms

from controller.forms.widgets import ReadOnlyBooleanWidget

from .models import Execution, Instance


class ExecutionInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExecutionInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            execution = kwargs.get('instance')
            if Execution.objects.filter(created_on__gt=execution.created_on,
                            operation=execution.operation, is_active=True).exists():
                self.fields['include_new_nodes'].widget = ReadOnlyBooleanWidget()


class ExecutionForm(forms.Form):
    retry_if_offline = forms.BooleanField(required=False, initial=True,
        help_text='The operation will be retried if the node is currently offline.')
    include_new_nodes = forms.BooleanField(required=False, help_text='If selected '
        'the operation will be executed on newly created nodes')
