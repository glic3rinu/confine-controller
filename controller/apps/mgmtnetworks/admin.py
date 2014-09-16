from __future__ import absolute_import

from permissions.admin import PermissionGenericTabularInline

from .forms import MgmtNetConfInlineForm
from .models import MgmtNetConf


class MgmtNetConfInline(PermissionGenericTabularInline):
    """ Management Network configuration inline """

    fields = ['backend', 'address']
    readonly_fields = ('address',)
    model = MgmtNetConf
    form = MgmtNetConfInlineForm
    max_num = 1
    can_delete = False
    verbose_name_plural = 'management network'

    def address(self, obj):
        return obj.addr.strNormal()

