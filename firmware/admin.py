from common.admin import get_modeladmin
from nodes.models import Node


def firmware_view(*args, **kwargs):
    pass


node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_link('firmware', firmware_view, 'Download Firmware', 'viewsitelink')
