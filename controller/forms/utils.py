from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe


def colored_field(value, colors):
    color = colors.get(value, "black")
    field = "<b><span style='color: %s;'>%s</span></b>" % (color, escape(value))
    return mark_safe(field)


def admin_link(rel, title=None):
    if not title:
        title = rel
    app_model = rel._meta.db_table
    url = reverse('admin:%s_change' % app_model, args=(rel.pk,))
    return mark_safe("<a href='%s'>%s</a>" % (url, title))

