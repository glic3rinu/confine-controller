from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import escape
from utils import get_field_value

def insert_inline(model, inline, head=False):
    """ Insert model inline into an existing model_admin """
    
    model_admin = admin.site._registry[model]
    if hasattr(inline, 'inline_identify'):
        delete_inline(model, inline.inline_identify)
    # Avoid inlines defined on parent class be shared between subclasses
    # Seems that if we use tuples they are lost in some conditions like changing
    # the tuple in modeladmin.__init__ 
    if not model_admin.inlines: model_admin.__class__.inlines = []
    if head:
        model_admin.inlines = [inline] + model_admin.inlines
    else:
        model_admin.inlines.append(inline)


def insert_list_filter(model, filter):
    model_admin = admin.site._registry[model]
    if not model_admin.list_filter: model_admin.__class__.list_filter = []
    model_admin.list_filter += (filter,)


def insert_list_display(model, field):
    model_admin = admin.site._registry[model]
    if not model_admin.list_display: model_admin.__class__.list_display = []
    model_admin.list_display += (field,)    


def link(attribute, description='', admin_order_field=True, base_url=''):
    def admin_link(obj, attr=attribute):
        url = get_field_value(obj, attr)
        link_url = "%s%s" % (base_url,url) if base_url else url
        return '<a href="%s">%s' % (link_url, url)
    admin_link.short_description = description if description else attribute.capitalize()
    admin_link.allow_tags = True

    if admin_order_field:
        admin_link.admin_order_field = attribute

    return admin_link


def admin_link(field_name, app_model='auth_user'):
    def link(obj, field=field_name):
        rel = get_field_value(obj, field)
        if not rel: return ''
        url = reverse('admin:%s_change' % app_model, args=(rel.pk,))
        return '<a href="%s">%s</a>' % (url, rel)
    link.short_description = field_name.capitalize()
    link.allow_tags = True
    link.admin_order_field = field_name
    
    return link


def colored(field_name, colours, description=''):
    def colored_field(obj, field=field_name, colors=colours):
        value = escape(get_field_value(obj, field))
        color = colors.get(value, "black")
        return """<b><span style="color: %s;">%s</span></b>""" % (color, value)
    if not description: description = field_name.split('__').pop().replace('_', ' ').capitalize()
    colored_field.short_description = description
    colored_field.allow_tags = True
    colored_field.admin_order_field = field_name
    
    return colored_field
