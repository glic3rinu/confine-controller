from __future__ import unicode_literals

from functools import update_wrapper

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.shortcuts import redirect
from django.utils.html import escape
from django.utils.importlib import import_module
from django.utils.safestring import mark_safe

from controller.models.utils import get_field_value
from controller.utils.time import timesince, timeuntil


def get_modeladmin(model, run_import_module=True):
    """ returns the modeladmin registered for model """
    model_admin = admin.site._registry.get(model, None)
    if model_admin is None and run_import_module:
        # Sometimes the admin module is not yet imported
        import_module(model.__module__.replace('.models', '.admin'))
        model_admin = admin.site._registry.get(model, None)
    return model_admin


def insertattr(model, name, value, weight=0):
    is_model = models.Model in model.__mro__
    modeladmin = get_modeladmin(model) if is_model else model
    # Avoid inlines defined on parent class be shared between subclasses
    # Seems that if we use tuples they are lost in some conditions like changing
    # the tuple in modeladmin.__init__
    if not getattr(modeladmin, name):
        setattr(type(modeladmin), name, [])
    
    inserted_attrs = getattr(modeladmin, '__inserted_attrs__', {})
    if not name in inserted_attrs:
        weights = {}
        if hasattr(modeladmin, 'weights') and name in modeladmin.weights:
            weights = modeladmin.weights.get(name)
        inserted_attrs[name] = [ (attr, weights.get(attr, 0)) for attr in getattr(modeladmin, name) ]
    
    inserted_attrs[name].append((value, weight))
    inserted_attrs[name].sort(key=lambda a: a[1])
    setattr(modeladmin, name, [ attr[0] for attr in inserted_attrs[name] ])
    setattr(modeladmin, '__inserted_attrs__', inserted_attrs)


def insert_change_view_action(model, action):
    """ inserts action to modeladmin.change_view_actions """
    is_model = models.Model in model.__mro__
    modeladmin = get_modeladmin(model) if is_model else model
    modeladmin.set_change_view_action(action)


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
    admin_link.short_description = description or attribute.capitalize()
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
        if field == '':
            rel = obj
        else:
            rel = get_field_value(obj, field)
        if not rel:
            return ''
        if not app_model:
            app_model = rel._meta.db_table
        url = reverse('admin:%s_change' % app_model, args=(rel.pk,))
        if not href_name:
            href_name = rel
        return mark_safe("<a href='%s'>%s</a>" % (url, href_name))
    link.short_description = field_name.capitalize()
    link.allow_tags = True
    link.admin_order_field = field_name
    return link


def get_admin_link(obj, href_name=''):
    """ returns the admin change view of obj formatted as url """
    return admin_link('', href_name=href_name)(obj)


def colored(field_name, colours, description='', verbose=False, bold=True):
    """ returns a method that will render obj with colored html """
    def colored_field(obj, field=field_name, colors=colours, verbose=verbose):
        value = escape(get_field_value(obj, field))
        color = colors.get(value, "black")
        if verbose:
            # Get the human-readable value of a choice field
            value = getattr(obj, 'get_%s_display' % field)()
        colored_value = '<span style="color: %s;">%s</span>' % (color, value)
        if bold:
            colored_value = '<b>%s</b>' % colored_value
        return mark_safe(colored_value)
    if not description:
        description = field_name.split('__').pop().replace('_', ' ').capitalize()
    colored_field.short_description = description
    colored_field.allow_tags = True
    colored_field.admin_order_field = field_name
    return colored_field


def action_to_view(action, modeladmin):
    """ Converts modeladmin action to view function """
    def action_view(request, object_id=1, modeladmin=modeladmin, action=action):
        queryset = modeladmin.model.objects.filter(pk=object_id)
        response = action(modeladmin, request, queryset)
        if not response:
            opts = modeladmin.model._meta
            url = 'admin:%s_%s_change' % (opts.app_label, opts.model_name)
            return redirect(url, object_id)
        return response
    return action_view


def wrap_admin_view(modeladmin, view):
    """ Add admin authentication to view """
    def wrapper(*args, **kwargs):
        return modeladmin.admin_site.admin_view(view)(*args, **kwargs)
    return update_wrapper(wrapper, view)


def docstring_as_help_tip(cls):
    """ return cls docstring as html help tip for use in admin """
    docstring = ' '.join([line.strip() for line in cls.__doc__.splitlines()])
    img = ('<img src="/static/admin/img/icon-unknown.gif" class="help help-tooltip" '
           'width="10" height="10" alt="(%s)" title="%s"/>')
    return mark_safe(img % (docstring, docstring))


def set_default_filter(queryarg, request, value):
    """ set default filters for changelist_view """
    if not request.GET.has_key(queryarg):
        q = request.GET.copy()
        if callable(value):
            value = value(request)
        q[queryarg] = value
        request.GET = q
        request.META['QUERY_STRING'] = request.GET.urlencode()


def display_timesince(date, double=False):
    """ 
    Format date for messages create_on: show a relative time
    with contextual helper to show fulltime format.
    """
    if not date:
        return 'Never'
    date_rel = timesince(date)
    if not double:
        date_rel = date_rel.split(',')[0]
    date_rel += ' ago'
    date_abs = date.strftime("%Y-%m-%d %H:%M:%S %Z")
    return mark_safe("<span title='%s'>%s</span>" % (date_abs, date_rel))


def display_timeuntil(date):
    date_rel = timeuntil(date) + ' left'
    date_abs = date.strftime("%Y-%m-%d %H:%M:%S %Z")
    return mark_safe("<span title='%s'>%s</span>" % (date_abs, date_rel))
