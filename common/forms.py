from django.core.urlresolvers import reverse
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.utils.html import escape
from django.utils.safestring import mark_safe


def colored_field(value, colors):
    color = colors.get(value, "black")
    field = "<b><span style='color: %s;'>%s</span></b>" % (color, escape(value))
    return mark_safe(field)


def admin_link(rel, title=None):
    if not title: title = rel
    app_model = rel._meta.db_table
    url = reverse('admin:%s_change' % app_model, args=(rel.pk,))
    return mark_safe("<a href='%s'>%s</a>" % (url, title))


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

