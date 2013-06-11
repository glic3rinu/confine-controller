from django import template
from django.core.urlresolvers import reverse

from controller import get_version
from controller.utils import is_installed


register = template.Library()


@register.filter(name='isinstalled')
def app_is_installed(app_name):
    return is_installed(app_name)


@register.simple_tag(name="version")
def controller_version():
    return get_version()


@register.simple_tag(name="admin_url", takes_context=True)
def rest_to_admin_url(context):
    """ returns the admin equivelent url of the current REST API view """
    view = context['view']
    model = getattr(view, 'model', None)
    url = 'admin:index'
    args = []
    if model:
        url = 'admin:%s_%s' % (model._meta.app_label, model._meta.module_name)
        pk = view.kwargs.get(view.pk_url_kwarg)
        if pk:
            url += '_change'
            args = [pk]
        else:
            url += '_changelist'
    return reverse(url, args=args)
