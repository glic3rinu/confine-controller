from __future__ import absolute_import

from controller.admin.utils import insertattr, get_modeladmin
from nodes.models import Node, Server
from permissions.admin import PermissionGenericTabularInline

from .models import MgmtNetConf

class MgmtNetConfInline(PermissionGenericTabularInline):
    fields = ['backend', 'address']
    readonly_fields = ('address',)
    model = MgmtNetConf
    max_num = 1
    can_delete = False
    verbose_name_plural = 'management network'

    def address(self, obj):
        return obj.addr.strNormal()

