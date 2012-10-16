from common.admin import get_modeladmin
from nodes.models import Node


def firmware():
    pass

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('firmware', firmware, 'Download Firmware', 'viewsitelink')
