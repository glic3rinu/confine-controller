from __future__ import absolute_import

from controller.apps.permissions import RelatedPermission

from .models import Resource, ResourceReq


Resource.has_permission = RelatedPermission('content_object')
ResourceReq.has_permission = RelatedPermission('content_object')
