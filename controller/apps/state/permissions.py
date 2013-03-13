from __future__ import absolute_import

from permissions import RelatedPermission

from .models import NodeState


NodeState.has_permission = RelatedPermission('node')
