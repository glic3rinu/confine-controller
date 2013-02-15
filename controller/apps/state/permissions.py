from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import NodeState


NodeState.has_permission = ReadOnlyPermission()
