from __future__ import absolute_import

from controller.admin.utils import insertattr, insert_change_view_action, link
from nodes.models import Server, Node
from permissions.admin import PermissionGenericTabularInline

from .actions import cache_node_db
from .models import CnHost


class CnHostInline(PermissionGenericTabularInline):
    fields = ['app_url', 'cndb_uri', 'cndb_cached']
    readonly_fields = ['cndb_cached']
    model = CnHost
    max_num = 1
    verbose_name_plural = 'Community host'
    can_delete = False
     
    def cndb_cached(self, instance):
        date = instance.cndb_cached_on
        if not date:
            return 'Never'
        return date
    cndb_cached.short_description = 'CNDB cached on'


# Monkey-Patching Section

app_url_link = link('related_cnhost__app_url', description='CN URL')

insertattr(Node, 'actions', cache_node_db)
insert_change_view_action(Node, cache_node_db)

insertattr(Node, 'inlines', CnHostInline)
insertattr(Server, 'inlines', CnHostInline)
