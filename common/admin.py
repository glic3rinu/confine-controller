from django.contrib import admin
from django.core.urlresolvers import reverse

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


def link_factory(attribute, description='', admin_order_field=True, base_url=''):
    def link(obj, attr=attribute):
        url = getattr(obj, attr)
        link_url = "%s%s" % (base_url,url) if base_url else url
        return '<a href="%s">%s' % (link_url, url)
    link.short_description = description if description else attribute.capitalize()
    link.allow_tags = True

    if admin_order_field:
        link.admin_order_field = attribute

    return link


def admin_link_factory(field_name, app_model='auth_user'):
    def link(obj, field=field_name):
        rel = getattr(obj, field)
        if not rel: return ''
        url = reverse('admin:%s_change' % app_model, args=(rel.pk,))
        return '<a href="%s">%s</a>' % (url, rel)
    link.short_description = field_name.capitalize()
    link.allow_tags = True
    link.admin_order_field = field_name
    
    return link
