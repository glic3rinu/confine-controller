from django.db.models import Q


def get_user_tinchosts(user):
    """ Get a list user related tinc hosts PKs. """
    # user's hosts
    hosts = user.tinc_hosts.values_list('related_tinc__pk', flat=True)
    # nodes of the user's groups where is group or node admin
    nodes = user.groups.filter(
                Q(roles__is_group_admin=True) |
                Q(roles__is_node_admin=True)
            ).exclude(nodes__isnull=True
            ).values_list('nodes__related_tinc__pk', flat=True)
    return list(hosts) + list(nodes)
