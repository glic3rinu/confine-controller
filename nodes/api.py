from nodes import models as node_models
from nodes import settings as node_settings

def create_node(node_params = {}):
    """
    Provides a way to upload a non-active node. It accepts a node_params
    as a hash, that will include all needed and extra node params
    Parameters accepted:
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
    Parameters accepted:
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
