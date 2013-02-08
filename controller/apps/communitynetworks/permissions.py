from __future__ import absolute_import

from permissions import AllowAllPermission

from .models import CnHost

# Since it uses generic relations we must relay that permissions will be 
# handled by the parent object
CnHost.has_permission = AllowAllPermission()
