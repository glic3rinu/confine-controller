# -*- coding: utf-8 -*-
import socket

import node_templates

from slices import models as slice_models

import paramiko

import settings

def load_slice_config(c_slice):
    """
    Returns slice config
    """
    slice_config = ""
    for sliver in c_slice.sliver_set.all():
        slice_config += load_sliver_config(sliver, True)[1] + "\n\n"
    return [int212hex(c_slice.id), slice_config]

def load_sliver_config(sl, use_complete_id = False):
    """
    Returns sliver config
    """
    sliver_id = int212hex(sl.slice.id)
    complete_sliver_id = "%s_%s" % (sliver_id, sl.node.hex_id)

    if use_complete_id:
        current_id = complete_sliver_id
    else:
        current_id = sliver_id
    
    interfaces = ""
    for request in sl.networkrequest_set.all():
        if request.number:
            interfaces += node_templates.SLIVER_INTERFACE_TYPE % {'number': "%.2i" % request.number, 'type': request.type}
            interfaces += node_templates.SLIVER_INTERFACE_NAME % {'number': "%.2i" % request.number, 'name': request.interface.name} if request.interface else ""
            interfaces += node_templates.SLIVER_INTERFACE_IPV4_PROTO % {'number': "%.2i" % request.number, 'proto': 'static'}
            interfaces += node_templates.SLIVER_INTERFACE_IPV4 % {'number': "%.2i" % request.number, 'ip': request.ipv4_address}
            interfaces += node_templates.SLIVER_INTERFACE_IPV6_PROTO % {'number': "%.2i" % request.number, 'proto': 'static'}
            interfaces += node_templates.SLIVER_INTERFACE_IPV6 % {'number': "%.2i" % request.number, 'ip': request.ipv6_address}
            interfaces += node_templates.SLIVER_INTERFACE_MAC % {'number': "%.2i" % request.number, 'mac': request.mac_address}

    fs_template_uri = ""
    if sl.slice.template:
        fs_template_url = sl.slice.template.data_uri
    sliver_config = node_templates.NODE_CONFIG_TEMPLATE % {
        'sliver_id': current_id,
        'ssh_key': sl.slice.user.get_profile().ssh_key,
        'fs_template_url': fs_template_uri,
        'exp_data_url': 'http://distro.confine-project.eu/misc/openwrt-exp-data.tgz',
        'interfaces': interfaces
        }
    return [sliver_id, sliver_config]

def get_interface_number(line):
    """
    This function is a helper to retrieve an interface number from
    standar UCI lines
    """
    return int(line.split(" ")[1].split("_")[0].replace("if", ""))

def process_sliver_status(sliver_status, node):
    """
    This function will process return of sliver status from node
    """
    slice_id = None
    sliver_nr = None
    ipv4 = {}
    ipv6 = {}
    mac = {}
    current_state = None
    for line in sliver_status.split("\n"):
        line = line.strip()
        if u"config sliver" in line:
            slice_id = hex2int(line.split(" ")[-1].replace("'", ""))
        elif u"sliver_nr" in line:
            sliver_nr = int(line.split(" ")[-1].replace("'", ""))
        elif u"ipv4" in line and u"proto" not in line:
            iface = get_interface_number(line)
            ipv4[iface] = line.split(" ")[-1].replace("'", "")
        elif u"ipv6" in line and u"proto" not in line:
            iface = get_interface_number(line)
            ipv6[iface] = line.split(" ")[-1].replace("'", "")
        elif u"mac" in line:
            iface = get_interface_number(line)
            mac[iface] = line.split(" ")[-1].replace("'", "")
        elif u"state" in line:
            current_state = line.split(" ")[-1].replace("'", "")

    sliver = slice_models.Sliver.objects.get(node = node, slice__id = slice_id)
    sliver.number = sliver_nr
    sliver.state = current_state
    sliver.save()
    network_reqs = sliver.networkrequest_set.all()
    for nq in network_reqs:
        if nq.number in mac.keys():
            nq.mac_address = mac[nq.number]
        if nq.number in ipv4.keys():
            nq.ipv4_address = ipv4[nq.number]
        if nq.number in ipv6.keys():
            nq.ipv6_address = ipv6[nq.number]
        nq.save()

def load_node_config(node):
    """
    Returns node config with all of its slices
    """
    slivers = slice_models.Sliver.objects.filter(node__id = node.id)
    node_config = []
    interfaces = ""
    ifnumber = 1

    for sl in slivers:
        node_config.append(load_sliver_config(sl))
    return node_config

def send_node_config(node):
    """
    Sends node configuration (all slices) to node platform
    """
    config = load_node_config(node)
    for sliver_config in config:
        script = node_templates.SLIVER_SCRIPT % {
            'config': sliver_config[1], 'sliver_id': sliver_config[0]
            }
        return_data = ssh_connection(node.ipv6,
                                     settings.SERVER_PRIVATE_KEY,
                                     script)
        process_sliver_status(return_data, node)
    return True

def send_deploy_sliver(sliver):
    config = load_slice_config(sliver.slice)

    script = node_templates.SLICE_SCRIPT % {
        'config': config[1], 'slice_id': config[0]
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 settings.SERVER_PRIVATE_KEY,
                                 script)

def send_start_sliver(sliver):
    script = node_templates.SLIVER_START_SCRIPT % {
        'slice_id': int212hex(sliver.slice.id)
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 settings.SERVER_PRIVATE_KEY,
                                 script)

def send_stop_sliver(sliver):
    script = node_templates.SLIVER_STOP_SCRIPT % {
        'slice_id': int212hex(sliver.slice.id)
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 settings.SERVER_PRIVATE_KEY,
                                 script)

def ssh_connection(host, file_key, script, username = "root"):
    fkey = open(file_key, 'r')
    key = fkey.read()
    fkey.close()
    ssh = paramiko.SSHClient()
    nkey = paramiko.PKey(key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host,
                username = username,
                pkey = nkey)
    channel = ssh.get_transport().open_session()
    channel.exec_command(script)
    return channel.makefile('rb', -1).readlines()

def extract_params(xml_tree, params = []):
    """
    Return a hash with extracted params from xml tree
    """
    return_hash = {}
    for param in params:
        return_hash[param] = xml_tree.find(param).text
    return return_hash

def int212hex(cint):
    return "%.12X" % cint

def hex2int(chex):
    return int(chex, 16)
