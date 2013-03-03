from django import template

from controller.utils import is_installed


register = template.Library()


@register.filter(name='isinstalled')
def app_is_installed(app_name):
    return is_installed(app_name)
