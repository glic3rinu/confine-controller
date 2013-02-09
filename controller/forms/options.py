from django.forms.models import BaseInlineFormSet
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet


class RequiredInlineFormSetMixin(object):
    """
    Generates an inline formset that is required
    """
    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSetMixin, self)._construct_form(i, **kwargs)
        form.empty_permitted = (i == 1)
        return form


class RequiredGenericInlineFormSet(RequiredInlineFormSetMixin, BaseGenericInlineFormSet):
    pass


class RequiredInlineFormSet(RequiredInlineFormSetMixin, BaseInlineFormSet):
    pass
