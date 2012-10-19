from common.admin import get_modeladmin
from firmware.actions import get_firmware
from nodes.models import Node


node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('firmware', get_firmware, 'Download Firmware', 'viewsitelink')
