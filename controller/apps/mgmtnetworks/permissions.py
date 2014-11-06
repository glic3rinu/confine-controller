from __future__ import absolute_import

from permissions import AllowAllPermission

from .models import MgmtNetConf


# Since it uses generic relations we must relay that permissions will be
# handled by the parent object
MgmtNetConf.has_permission = AllowAllPermission()
