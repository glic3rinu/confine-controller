from nodes import models as node_models
from slices import models as slice_models
from user_management import models as user_management_models
from nodes import settings as node_settings
from nodes import node_utils

from django.db import transaction, IntegrityError

def get_node(node_params = {}):
    """
    Retrieve a node
    - id
    """
    id = node_params.get('id', '')
    try:
        node = node_models.Node.objects.get(id = id)
        return node
    except:
        pass
    return None

def edit_node(node_params = {}):
    """
    Edit a node. Data provided is through objects.
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
    node.interface_set.all().delete()
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
    - rd_arch
    - admin
    - rd_uuid
    - rd_pubkey
    - rd_cert
    - rd_boot_sn
    - nodeprops
    -- name
    -- value
    """
    hostname = node_params.get('hostname', '')
    ip = node_params.get('ip', '')
    rd_arch = node_params.get('rd_arch', '')
    admin = node_params.get('admin', None)
    rd_uuid = node_params.get('rd_uuid', '')
    rd_pubkey = node_params.get('rd_pubkey', '')
    rd_cert = node_params.get('rd_cert', '')
    rd_boot_sn = node_params.get('rd_boot_sn')
    nodeprops = node_params.get('nodeprops', [])
    try:
        node = node_models.Node(hostname = hostname,
                                ip = ip,
                                rd_arch = rd_arch,
                                admin = admin,
                                rd_uuid = rd_uuid,
                                rd_pubkey = rd_pubkey,
                                rd_cert = rd_cert,
                                rd_boot_sn = rd_boot_sn
                                )
        
        node.save()
        for np in nodeprops:
            nodeprop = node_models.NodeProps(name = np.get('name', 'missing name'),
                                             value = np.get('value', 'missing value')
                                             )
            nodeprop.node = node
            nodeprop.save()
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
    - id
    """
    id = node_params.get('id', '')

    try:
        if id:
            node = node_models.Node.objects.get(id = id)
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
    - template
    - vlan_nr
    - exp_data_uri
    - exp_data_sha256
    - uuid
    - pubkey
    - expires
    - instance_sn
    - new_sliver_instance_sn
    """
    user = slice_params.get('user', None)
    nodes = slice_params.get('nodes', [])
    name = slice_params.get('name', '')
    template = slice_params.get('template', None)
    vlan_nr = slice_params.get('vlan_nr', None)
    exp_data_uri = slice_params.get('exp_data_uri', None)
    exp_data_sha256 = slice_params.get('exp_data_sha256', None)
    uuid = slice_params.get('uuid', None)
    pubkey = slice_params.get('pubkey', None)
    expires = slice_params.get('expires', None)
    instance_sn = slice_params.get('instance_sn', None)
    new_sliver_instance_sn = slice_params.get('new_sliver_instance_sn', None)

    if user and len(nodes) > 0:
        c_slice = slice_models.Slice(name = name,
                                     user = user,
                                     vlan_nr = vlan_nr,
                                     exp_data_uri = exp_data_uri,
                                     exp_data_sha256 = exp_data_sha256,
                                     uuid = uuid,
                                     pubkey = pubkey,
                                     expires = expires,
                                     instance_sn = instance_sn,
                                     new_sliver_instance_sn = new_sliver_instance_sn)
        if template:
            c_slice.template_id = template
        c_slice.save()
        for node in nodes.keys():
            c_node = node_models.Node.objects.get(id = node)
            c_sliver = slice_models.Sliver(slice = c_slice,
                                           node = c_node,
                                           instance_sn = instance_sn)
            c_sliver.save()


            for extra in ['cpu', 'storage', 'memory']:
                ext = nodes[node][extra]
                if ext:
                    ext.sliver = c_sliver
                    ext.save()
                    
            ii = nodes[node]['ii']
            if len(ii) > 0:
                for isolatedinterface in ii:
                    isolatedinterface.sliver = c_sliver
                    isolatedinterface.save()
            pubi = nodes[node]['pubi']
            if len(pubi) > 0:
                for publicinterface in pubi:
                    publicinterface.sliver = c_sliver
                    publicinterface.save()
            privi = nodes[node]['privi']
            if len(privi) > 0:
                for privateinterface in privi:
                    privateinterface.sliver = c_sliver
                    privateinterface.save()
                    
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
    - id
    """
    id = node_params.get("id", None)
    try:
        node = node_models.Node.objects.get(id = id)
        return node_utils.load_node_config(node)
    except:
        pass
    return None

def get_node_public_keys(node_params = {}):
    """
    Provides a way to retrieve all public keys related
    to a given node
    Accepted parameters:
    - id
    """
    id = node_params.get("id", None)
    try:
        slices = slice_models.Slice.objects.filter(sliver__node__id = id)
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

def delete_slices(slice_params = {}):
    """
    Delete given slices with all slivers
    - slice_slug
    """
    slice_slug = slice_params.get('slice_slug', None)
    if slice_slug:
        c_slice = slice_models.Slice.objects.get(slug = slice_slug)
        slivers = c_slice.sliver_set.all()
        delete_slivers({'slivers': slivers})
        c_slice.delete()
        return True
    return False

def allocate_slivers(node_params = {}):
    """
    Allocate all slivers from a given node
    - node
    - node_id
    """
    node = node_params.get("node", None)
    if node:
        return node_utils.send_node_config(node)
        return True
    else:
        node_id = node_params.get("node_id", None)
        if node_id:
            node = node_models.Node.objects.get(id = node_id)
            return node_utils.send_node_config(node)
            return True
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

def delete_slivers(sliver_params = {}):
    """
    Stop given slivers
    - sliver_id
    - slivers
    """
    sliver_id = sliver_params.get('sliver_id', None)
    slivers = sliver_params.get('slivers', [])
    if sliver_id:
        sliver = slice_models.Sliver.objects.get(id = sliver_id)
        accum = node_utils.send_remove_sliver(sliver)
        sliver.delete()
        return accum
    elif slivers:
        accum = []
        for sliver in slivers:
            accum.append(node_utils.send_remove_sliver(sliver))
            sliver.delete()
        return accum
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


def create_research_group(research_group_params = {}):
    """
    Creates a new research group
    - name
    """
    name = research_group_params.get('name', '')
    if name:
        research_group = user_management_models.ResearchGroup(name = name)
        try:
            sid = transaction.savepoint()
            research_group.save()
            transaction.savepoint_commit(sid)
            return True
        except IntegrityError:
            transaction.savepoint_rollback(sid)
    return False
