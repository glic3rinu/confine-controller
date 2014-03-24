from __future__ import absolute_import

from controller.admin.utils import insertattr, get_modeladmin
from nodes.models import Node, Server
from mgmtnetworks.tinc.models import Host, Gateway
from permissions.admin import PermissionGenericTabularInline

from .models import MgmtNetConf

class MgmtNetConfInline(PermissionGenericTabularInline):
    fields = ['backend', 'addr']
    readonly_fields = ('addr',)
    model = MgmtNetConf
    max_num = 1
    can_delete = False
    verbose_name_plural = 'management network'


# Monkey-Patching Section

for model in [Node, Server, Gateway, Host]:
    insertattr(model, 'inlines', MgmtNetConfInline)
