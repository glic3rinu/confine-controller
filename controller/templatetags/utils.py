from django import template

from controller import get_version
from controller.utils import is_installed


register = template.Library()


@register.filter(name='isinstalled')
def app_is_installed(app_name):
    return is_installed(app_name)


@register.simple_tag(name="version")
def controller_version():
    return get_version()
