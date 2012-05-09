from nodes import models as node_models
from slices import models as slice_models
from nodes import settings as node_settings
from nodes import node_utils

def create_node(node_params = {}):
    """
    Provides a way to upload a non-active node. It accepts a node_params
    as a hash, that will include all needed and extra node params
    Accepted parameters:
    - hostname
    - ip
    - architecture
    """
    hostname = node_params.get('hostname', '')
    ip = node_params.get('ip', '')
    architecture = node_params.get('architecture', '')

    try:
        node = node_models.Node(hostname = hostname,
                                ip = ip,
                                architecture = architecture,
                                state = node_settings.PROJECTED)
        
        node.save()
    except:
        return False
    return True

def delete_node(node_params = {}):
    """
    Provides a way to request a delete of a given node. It accepts a node_params
    as a hash, that will include needed node params
    Accepted parameters:
    - hostname
    - ip
    """
    hostname = node_params.get('hostname', '')
    ip = node_params.get('ip', '')

    try:
        if hostname:
            node = node_models.Node.objects.get(hostname = hostname)
        elif ip:
            node = node_models.Node.objects.get(ip = ip)
        else:
            raise Exception("Missing needed params")
        delete_request = node_models.DeleteRequest(node = node)
        delete_request.save()
    except:
        return False
    return True

def create_slice(slice_params = {}):
    """
    This function provides a way to create an slice, and notify its creation
    to node.
    Accepted parameters:
    - nodes (list of node_id)
    - user
    - name 
    """
    user = slice_params.get('user', None)
    nodes = slice_params.get('nodes', [])
    name = slice_params.get('name', '')
    
    if user and len(nodes) > 0:
        c_slice = slice_models.Slice(name = name,
                                     user = user)
        c_slice.save()
        for node in nodes:
            c_node = node_models.Node.objects.get(id = node)
            c_sliver = slice_models.Sliver(slice = c_slice,
                                           node = c_node)
            c_sliver.save()
            #node_utils.send_node_config(c_node)
        return True
    return False

def show_slices(slice_params = {}):
    """
    Provides all slices that a given user belongs to
    Accepted parameters:
    - user
    """

    user = slice_params.get("user", None)

    if user:
        return user.slice_set.all()
    return []
