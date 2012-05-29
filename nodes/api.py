from nodes import models as node_models
from slices import models as slice_models
from nodes import settings as node_settings
from nodes import node_utils

def get_node(node_params = {}):
    """
    Retrieve a node
    - hostname
    """
    hostname = node_params.get('hostname', '')
    try:
        node = node_models.objects.get(hostname = hostname)
        return node
    except:
        pass
    return None

def edit_node(node_params = {}):
    """
    Edit node
    """
    pass

def set_node(node_params = {}):
    """
    Set up a node. This is a clone method of create node, but data is not
    provided in a raw way but with objects
    - node
    - storage
    - memory
    - cpu
    - interfaces
    """
    node = node_params.get('node', '')
    storage = node_params.get('storage', '')
    memory = node_params.get('memory', '')
    cpu = node_params.get('cpu', '')
    interfaces = node_params.get('interfaces', '')

    node.save()
    if node.id:
        storage.node = node
        storage.save()
        memory.node = node
        memory.save()
        cpu.node = node
        cpu.save()
        for interface in interfaces:
            interface.node = node
            interface.save()
        return True
    return False

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

def get_nodes(node_params = {}):
    """
    Returns a list of current nodes
    """
    return node_models.Node.objects.all()

def delete_node(node_params = {}):
    """
    Provides a way to request a delete of a given node. It accepts a node_params
    as a hash, that will include needed node params
    Accepted parameters:
    - hostname
    """
    hostname = node_params.get('hostname', '')

    try:
        if hostname:
            node = node_models.Node.objects.get(hostname = hostname)
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
    - interfaces (list of interface_id)
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
        for node in nodes.keys():
            c_node = node_models.Node.objects.get(id = node)
            c_sliver = slice_models.Sliver(slice = c_slice,
                                           node = c_node)
            c_sliver.save()


            for extra in ['cpu', 'storage', 'memory']:
                ext = nodes[node][extra]
                if ext:
                    ext.sliver = c_sliver
                    ext.save()
            networks = nodes[node]['networks']
            if len(networks) > 0:
                for network in networks:
                    network.sliver = c_sliver
                    network.save()                
            allocate_slivers({'node': c_node})
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

def get_node_configuration(node_params = {}):
    """
    Provides a way to retrieve a node configuration
    through all slice config snippets.
    Accepted parameters:
    - hostname
    """
    hostname = node_params.get("hostname", None)
    try:
        node = node_models.Node.objects.get(hostname = hostname)
        return node_utils.load_node_config(node)
    except:
        pass
    return None

def get_node_public_keys(node_params = {}):
    """
    Provides a way to retrieve all public keys related
    to a given node
    Accepted parameters:
    - hostname
    """
    hostname = node_params.get("hostname", None)
    try:
        slices = slice_models.Slice.objects.filter(sliver__node__hostname = hostname)
        return map(lambda a: a.user.get_profile().ssh_key, slices)
    except:
        pass
    return None

def get_slice_public_keys(node_params = {}):
    """
    Provides a way to retrieve all public keys related
    to a given slice
    Accepted parameters:
    - name
    - slug
    """
    name = node_params.get("name", None)
    slug = node_params.get("slug", None)
    try:
        try:
            c_slice = slice_models.Slice.objects.get(name = name)
        except:
            c_slice = slice_models.Slice.objects.get(slug = slug)
        return [c_slice.user.get_profile().ssh_key]
    except:
        pass
    return []

def allocate_slivers(node_params = {}):
    """
    Allocate all slivers from a given node
    - node
    - node_id
    """
    node = node_params.get("node", None)
    if node:
        return node_utils.send_node_config(c_node)
    else:
        node_id = node_params.get("node_id", None)
        if node_id:
            node = node_models.Node.objects.get(id = node_id)
            return node_utils.send_node_config(c_node)
    return False
    

def deploy_slivers(sliver_params = {}):
    """
    Deploy given slivers
    - slice_slug
    """
    slice_slug = sliver_params.get('slice_slug', None)
    if slice_slug:
        slivers = slice_models.Sliver.objects.filter(slice__slug = slice_slug)
        for sliver in slivers:
            node_utils.send_deploy_sliver(sliver)
        return True
    return False

def start_slivers(sliver_params = {}):
    """
    Start given slivers
    - sliver_id
    """
    sliver_id = sliver_params.get('sliver_id', None)
    if sliver_id:
        sliver = slice_models.Sliver.objects.get(id = sliver_id)
        return node_utils.send_start_sliver(sliver)
    return False

def stop_slivers(sliver_params = {}):
    """
    Stop given slivers
    - sliver_id
    """
    sliver_id = sliver_params.get('sliver_id', None)
    if sliver_id:
        sliver = slice_models.Sliver.objects.get(id = sliver_id)
        return node_utils.send_stop_sliver(sliver)
    return False
