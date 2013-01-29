from django import template
from users.models import JoinRequest

register = template.Library()

@register.filter
def is_member(group, user):
    return group.is_member(user)

@register.filter
def has_join_request(group, user):
    return JoinRequest.objects.filter(group=group, user=user).exists()
