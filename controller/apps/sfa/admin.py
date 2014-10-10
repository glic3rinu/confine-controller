from __future__ import absolute_import

from controller.admin.utils import insertattr
from nodes.models import Node
from permissions.admin import PermissionGenericTabularInline
from slices.models import Slice
from users.models import User, Group

from .models import SfaObject


class SfaObjectInline(PermissionGenericTabularInline):
    fields = ('uuid', 'pubkey')
    model = SfaObject
    max_num = 1
    verbose_name_plural = 'SFA'
    
    def get_readonly_fields(self, request, obj=None):
        ro_fields = super(SfaObjectInline, self).get_readonly_fields(request, obj=obj)
        sfa = obj.sfa
        if obj.sfa is not None and 'uuid' not in ro_fields:
            return ro_fields + ('uuid',)
        return ro_fields


# Hook SfaObject support for related models

for model in [Slice, User, Group, Node]:
    insertattr(model, 'inlines', SfaObjectInline)
