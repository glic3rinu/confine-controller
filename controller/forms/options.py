from django.contrib.contenttypes.generic import BaseGenericInlineFormSet


class RequiredGenericInlineFormSet(BaseGenericInlineFormSet):
    """
    Generates an inline formset that is required
    """
    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredGenericInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form

