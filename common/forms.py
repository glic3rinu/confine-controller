from django.utils.html import escape
from django.utils.safestring import mark_safe

def colored_field(value, colors):
    color = colors.get(value, "black")
    field = "<b><span style='color: %s;'>%s</span></b>" % (color, escape(value))
    return mark_safe(field)
