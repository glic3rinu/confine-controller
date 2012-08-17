# -*- coding: utf-8 -*-
import socket

import re

import node_templates

import models as node_models

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

    for iface in sl.privateiface_set.all():
        interfaces += node_templates.SLIVER_INTERFACE_TYPE % {'number': "%.2i" % iface.nr, 'type': 'internal'}
        interfaces += node_templates.SLIVER_INTERFACE_NAME % {'number': "%.2i" % iface.nr, 'name': re.sub(r'\s', '', iface.name.lower())}

    for iface in sl.publiciface_set.all():
        interfaces += node_templates.SLIVER_INTERFACE_TYPE % {'number': "%.2i" % iface.nr, 'type': 'public'}
        interfaces += node_templates.SLIVER_INTERFACE_NAME % {'number': "%.2i" % iface.nr, 'name': re.sub(r'\s', '', iface.name.lower())}
        interfaces += node_templates.SLIVER_INTERFACE_IPV4_PROTO % {'number': "%.2i" % iface.nr, 'proto': 'dhcp'}

    for iface in sl.isolatediface_set.all():
        interfaces += node_templates.SLIVER_INTERFACE_TYPE % {'number': "%.2i" % iface.nr, 'type': 'isolated'}
        interfaces += node_templates.SLIVER_INTERFACE_NAME % {'number': "%.2i" % iface.nr, 'name': re.sub(r'\s', '', iface.name.lower())}
        interfaces += node_templates.SLIVER_INTERFACE_PARENT % {'number': "%.2i" % iface.nr, 'parent': iface.parent_name()}

    fs_template_uri = ""

    if sl.slice.template:
        fs_template_uri = sl.slice.template.data_uri
    sliver_config = node_templates.NODE_CONFIG_TEMPLATE % {
        'sliver_id': current_id,
        'ssh_key': sl.slice.user.get_profile().ssh_key,
        'fs_template_url': fs_template_uri,
        'exp_data_url': sl.slice.exp_data_uri,#'http://distro.confine-project.eu/misc/openwrt-exp-data.tgz',
        'exp_name': 'exp_name',
        'vlan_nr': int2hex(sl.slice.vlan_nr),
        'interfaces': interfaces
        }
    return [sliver_id, sliver_config]

def get_interface_number(line):
    """
    This function is a helper to retrieve an interface number from
    standar UCI lines
    """
    return int(line.split(" ")[1].split("_")[0].replace("if", ""))

def test_process_sliver_status():

    sliver_status = """
config sliver '00000000000a'
	option user_pubkey 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCVLzwx7V6PS+XzjELW4HmVsnpeVBztoidyyvXqNhK6qJl5g828AvDhHijcgvPICdLe1p1FAJXo7Wi5/5eqZ4QtY4Yf+QHVhzg3Z/lCg+gwlWeCVpUDDdyqbX/kgFirPCrAeDVd33dnHFg0S8jrum63rPE4ni5YhTL0/+3EFRKvDM7X6tL/SQRIYKEC+ECU3T1XZmgS353ViCoJaQsY/Gt8wyEnDunPkVV4dWgBYBASyNitPRVrWrq7pQiGGUAcJ4sMGNGoX9bGDOQfCYnAzKCw6b/FMTqDrYw+GAbUnYOL9s/1QAj+tz8gf+FjlZmKQeFg7I3TpeWKYdLBFSyB+RqT confine@vct'
	option exp_name 'hello-openwrt-experiment'
	option vlan_nr 'f0a'
	option fs_template_url 'http://distro.confine-project.eu/misc/CONFINE-sliver-openwrt-backfire-240612_1246.tar.gz'
	option exp_data_url 'http://distro.confine-project.eu/misc/exp-data-hello-world-openwrt.tgz'
	option sliver_nr '01'
	option if00_type 'internal'
	option if00_name 'priv'
	option if00_mac '54:c0:10:01:01:00'
	option if00_ipv4_proto 'static'
	option if00_ipv4 '192.168.241.1/25'
	option if00_ipv6_proto 'static'
	option if00_ipv6 'fdbd:e804:6aa9:0:0000:0000:000a:0/64'
	option if01_type 'public'
	option if01_name 'pub0'
	option if01_mac '54:c0:10:01:01:01'
	option if01_ipv6_proto 'static'
	option if01_ipv6 'fdf5:5351:1dfd:1001:0000:0000:000a:01/64'
	option if01_ipv4_proto 'dhcp'
	option if01_ipv4 '10.241.0.9/24'
	option if02_type 'isolated'
	option if02_name 'iso0'
	option if02_mac '54:c0:10:01:01:02'
	option if02_parent 'eth1'
	option state 'allocated'
    """
    sliver_status = sliver_status.split("\n")
    node = node_models.Node.objects.all()[0]
    process_sliver_status(sliver_status, node)

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
    for line in sliver_status:
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
    sliver.nr = sliver_nr
    sliver.state = current_state
    sliver.save()
    network_reqs = list(sliver.privateiface_set.all()) + list(sliver.publiciface_set.all()) + list(sliver.isolatediface_set.all())
    for nq in network_reqs:
        if nq.nr in mac.keys():
            nq.mac_addr = mac[nq.nr]
        if nq.nr in ipv4.keys():
            nq.ipv4_addr = ipv4[nq.nr]
        if nq.nr in ipv6.keys():
            nq.ipv6_addr = ipv6[nq.nr]
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

def test_node_config():
    """
    Test function
    """
    node = node_models.Node.objects.all()[0]
    config = load_node_config(node)
    scripts = []
    for sliver_config in config:
        script = node_templates.SLIVER_SCRIPT % {
            'config': sliver_config[1], 'sliver_id': sliver_config[0]
            }
        scripts.append(script)
    return scripts

def send_node_config(node):
    """
    Sends node configuration (all slices) to node platform
    """
    config = load_node_config(node)
    all_returned_data = []
    for sliver_config in config:
        script = node_templates.SLIVER_SCRIPT % {
            'config': sliver_config[1], 'sliver_id': sliver_config[0]
            }
        import pdb; pdb.set_trace()
        return_data = ssh_connection(node.ipv6,
                                                 settings.SERVER_PRIVATE_KEY,
                                                 script)
        all_returned_data.append(return_data)
        import pdb; pdb.set_trace()
        process_sliver_status(return_data[0], node)
    return [True, all_returned_data]

def send_deploy_sliver(sliver):
    config = load_slice_config(sliver.slice)

    script = node_templates.SLICE_SCRIPT % {
        'config': config[1], 'slice_id': config[0]
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 settings.SERVER_PRIVATE_KEY,
                                 script)
    return return_data
def send_start_sliver(sliver):
    script = node_templates.SLIVER_START_SCRIPT % {
        'slice_id': int212hex(sliver.slice.id)
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 settings.SERVER_PRIVATE_KEY,
                                 script)
    return return_data

def send_stop_sliver(sliver):
    script = node_templates.SLIVER_STOP_SCRIPT % {
        'slice_id': int212hex(sliver.slice.id)
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 settings.SERVER_PRIVATE_KEY,
                                 script)
    return return_data

def send_remove_sliver(sliver):
    script = node_templates.SLIVER_REMOVE_SCRIPT % {
        'slice_id': int212hex(sliver.slice.id)
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 settings.SERVER_PRIVATE_KEY,
                                 script)
    return return_data

def ssh_connection(host, file_key, script, username = "root", password = "confine"):
    #fkey = open(file_key, 'r')
    #key = fkey.read()
    #fkey.close()
    ssh = paramiko.SSHClient()
    #nkey = paramiko.PKey(key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect(host,
    #            username = username,
    #            pkey = nkey)
    ssh.connect(host,
                username = username,
                password = password)
                
    channel = ssh.get_transport().open_session()
    channel.exec_command(script)
    return_data = channel.makefile('rb', -1).readlines()
    error_data = channel.makefile_stderr('rb', -1).readlines()
    return [return_data, error_data]

def extract_params(xml_tree, params = []):
    """
    Return a hash with extracted params from xml tree
    """
    return_hash = {}
    for param in params:
        return_hash[param] = xml_tree.find(param).text
    return return_hash

def int212hex(cint):
    return ("%.12x" % cint)

def hex2int(chex):
    return int(chex, 16)

def int2hex(cint):
    return ("%x" % cint)
