from __future__ import absolute_import

from controller.apps.permissions import RelatedPermission

from .models import NodeGeolocation

NodeGeolocation.has_permission = RelatedPermission('node')
