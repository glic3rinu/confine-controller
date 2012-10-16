from common.admin import get_modeladmin, action_as_view
from nodes.models import Node


node_modeladmin = get_modeladmin(Node)

def firmware_view(request, object_id, modeladmin=node_modeladmin):
    #return action_as_view(firmware, modeladmin, request, object_id)
    pass

node_modeladmin.set_change_view_link('firmware', firmware_view, 'Download Firmware', 'viewsitelink')
