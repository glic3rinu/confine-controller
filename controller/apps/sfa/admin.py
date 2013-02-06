from __future__ import absolute_import

from controller.admin.utils import insert_inline
from nodes.models import Node
from permissions.admin import PermissionGenericTabularInline
from slices.models import Slice
from users.models import User, Group

from .models import SfaObject


class SfaObjectInline(PermissionGenericTabularInline):
    model = SfaObject
    max_num = 1
    verbose_name_plural = 'SFA'


# Hook SfaObject support for related models

for model in [Slice, User, Group, Node]:
    insert_inline(model, SfaObjectInline)
