import re

from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe

from controller import get_version
from controller.utils.apps import is_installed


register = template.Library()


@register.filter(name='isinstalled')
def app_is_installed(app_name):
    return is_installed(app_name)


@register.simple_tag(name="version")
def controller_version():
    return get_version()

@register.assignment_tag()
def get(array, index):
    """
    Allow variable index access in templates
    http://code.djangoproject.com/ticket/3371
    """
    try:
        return array[index]
    except IndexError:
        return None

@register.simple_tag(name="admin_url", takes_context=True)
def rest_to_admin_url(context):
    """ returns the admin equivalent url of the current REST API view """
    view = context['view']
    model = getattr(view, 'model', None)
    url = 'admin:index'
    args = []
    if model:
        url = 'admin:%s_%s' % (model._meta.app_label, model._meta.model_name)
        pk = view.kwargs.get(view.pk_url_kwarg)
        if pk:
            url += '_change'
            args = [pk]
        else:
            url += '_changelist'
    try:
        return reverse(url, args=args)
    except NoReverseMatch:
        return reverse('admin:index')


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)


@register.filter(name="compact")
def compact(text):
    compacted = text.replace('\n', '').replace('<p>', '<br>').replace('</p>', '</br>')
    compacted = re.sub('^<br>', '', compacted) 
    return mark_safe(compacted)


@register.filter(name='content_type')
def content_type(obj):
    return ContentType.objects.get_for_model(type(obj)).pk
