from django import forms

from controller.forms.widgets import ReadOnlyBooleanWidget

from .models import Execution, Instance


class ExecutionInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExecutionInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            execution = kwargs.get('instance')
#            if not execution.state == Execution.PROGRESS:
#            self.fields['is_active'].widget = ReadOnlyBooleanWidget()
            if Execution.objects.filter(created_on__gt=execution.created_on,
                                        operation=execution.operation,
                                        is_active=True).exists():
                self.fields['include_new_nodes'].widget = ReadOnlyBooleanWidget()


class ExecutionForm(forms.Form):
    include_new_nodes = forms.BooleanField(required=False, help_text='If selected '
        'the operation will be executed on newly created nodes')
