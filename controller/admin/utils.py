from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.functional import update_wrapper
from django.utils.html import escape
from django.utils.safestring import mark_safe

from controller.models.utils import get_field_value


def get_modeladmin(model):
    """ return the model registred ModelAdmin """
    for k,v in admin.site._registry.iteritems():
        if k is model: return v


def insert_inline(model, inline, head=False):
    """ Insert model inline into an existing model_admin """
    model_admin = get_modeladmin(model)
    if hasattr(inline, 'inline_identify'):
        delete_inline(model, inline.inline_identify)
    # Avoid inlines defined on parent class be shared between subclasses
    # Seems that if we use tuples they are lost in some conditions like changing
    # the tuple in modeladmin.__init__ 
    if not model_admin.inlines: type(model_admin).inlines = []
    if head:
        model_admin.inlines = [inline] + model_admin.inlines
    else:
        model_admin.inlines.append(inline)


def insert_list_filter(model, filter):
    """ insert filter to modeladmin.list_filters """
    model_admin = get_modeladmin(model)
    if not model_admin.list_filter: type(model_admin).list_filter = []
    model_admin.list_filter += (filter,)


def insert_list_display(model, field):
    """ insert field to modeladmin.list_display """
    model_admin = get_modeladmin(model)
    if not model_admin.list_display: type(model_admin).list_display = []
    model_admin.list_display += (field,)    


def insert_action(model, action):
    """ insert action to modeladmin.actions """
    model_admin = get_modeladmin(model)
    if not model_admin.actions: type(model_admin).actions = [action]
    else: model_admin.actions.append(action)


def link(attribute, description='', admin_order_field=True, base_url=''):
    """
    Returns a function that will yield its obj.attribute formatted as url
    Useful for printing hrefs on ModelAdmin.list_display
    """
    def admin_link(obj, attr=attribute):
        try: 
            url = get_field_value(obj, attr)
        except: 
            return ''
        link_url = "%s%s" % (base_url, url) if base_url else url
        return '<a href="%s">%s' % (link_url, url)
    admin_link.short_description = description if description else attribute.capitalize()
    admin_link.allow_tags = True
    
    if admin_order_field:
        admin_link.admin_order_field = attribute
    
    return admin_link


def admin_link(field_name, app_model='', href_name=''):
    """ 
    Returns a function that will yield the admin url of obj.field_name
    Useful for specify a ModelAdmin.list_display member
    """
    def link(obj, field=field_name, app_model=app_model, href_name=href_name):
        if field == '': rel = obj
        else:
            rel = get_field_value(obj, field)
        if not rel: return ''
        if not app_model: app_model = rel._meta.db_table
        url = reverse('admin:%s_change' % app_model, args=(rel.pk,))
        if not href_name: href_name = rel
        return mark_safe("<a href='%s'>%s</a>" % (url, href_name))
    link.short_description = field_name.capitalize()
    link.allow_tags = True
    link.admin_order_field = field_name
    
    return link


def get_admin_link(obj, href_name=''):
    """ return the admin change view of obj formatted as url """
    return admin_link('', href_name=href_name)(obj)


def colored(field_name, colours, description='', verbose=False):
    """ return a method that will render obj with colored html """
    def colored_field(obj, field=field_name, colors=colours, verbose=verbose):
        value = escape(get_field_value(obj, field))
        color = colors.get(value, "black")
        if verbose:
            # Get the human-readable value of a choice field
            value = getattr(obj, 'get_%s_display' % field)()
        return """<b><span style="color: %s;">%s</span></b>""" % (color, value)
    if not description: description = field_name.split('__').pop().replace('_', ' ').capitalize()
    colored_field.short_description = description
    colored_field.allow_tags = True
    colored_field.admin_order_field = field_name
    
    return colored_field


def action_to_view(action, modeladmin):
    """ Convert modeladmin action as to view function """
    def action_view(request, object_id, modeladmin=modeladmin, action=action):
        queryset = modeladmin.model.objects.filter(pk=object_id)
        response = action(modeladmin, request, queryset)
        if not response:
            opts = modeladmin.model._meta
            return HttpResponseRedirect(reverse('admin:%s_%s_change' % (opts.app_label, opts.module_name), args=[object_id]))
        return response
    return action_view


def wrap_admin_view(modeladmin, view):
    """ Add admin authentication to view """
    def wrapper(*args, **kwargs):
        return modeladmin.admin_site.admin_view(view)(*args, **kwargs)
    return update_wrapper(wrapper, view)


def docstring_as_help_tip(cls):
    """ return cls docstring as html help tip for use in admin """
    docstring = cls.__doc__.strip()
    img = '<img src="/static/admin/img/icon-unknown.gif" class="help help-tooltip" width="10" height="10" alt="(%s)" title="%s"/>'
    return mark_safe(img % (docstring, docstring))