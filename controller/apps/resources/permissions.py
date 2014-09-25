from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import Resource, ResourceReq


Resource.has_permission = ReadOnlyPermission()
ResourceReq.has_permission = ReadOnlyPermission()
