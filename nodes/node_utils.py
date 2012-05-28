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
        pass
    return ["%.12i" % c_slice.id, slice_config]

def load_sliver_config(sl):
    """
    Returns sliver config
    """
    interfaces = ""
    for request in sl.networkrequest_set.all():
        interfaces += node_templates.SLIVER_INTERFACE_TYPE % {'number': request.number, 'type': request.type}
        interfaces += node_templates.SLIVER_INTERFACE_NAME % {'number': request.number, 'name': request.interface.name} if request.interface else ""
        interfaces += node_templates.SLIVER_INTERFACE_IPV4_PROTO % {'number': request.number, 'proto': 'static'}
        interfaces += node_templates.SLIVER_INTERFACE_IPV4 % {'number': request.number, 'ip': request.ipv4_address}
        interfaces += node_templates.SLIVER_INTERFACE_IPV6_PROTO % {'number': request.number, 'proto': 'static'}
        interfaces += node_templates.SLIVER_INTERFACE_IPV6 % {'number': request.number, 'ip': request.ipv6_address}
        interfaces += node_templates.SLIVER_INTERFACE_MAC % {'number': request.number, 'mac': request.mac_address}
    sliver_config = node_templates.NODE_CONFIG_TEMPLATE % {
        'sliver_id': "%.12i" % sl.slice.id,
        'ssh_key': sl.slice.user.get_profile().ssh_key,
        'fs_template_url': 'http://downloads.openwrt.org/backfire/10.03.1-rc6/x86_generic/openwrt-x86-generic-rootfs.tar.gz',
        'exp_data_url': 'http://distro.confine-project.eu/misc/openwrt-exp-data.tgz',
        'interfaces': interfaces
        }
    return ["%.12i" % sl.slice.id, sliver_config]

def process_sliver_status(sliver_status):
    """
    This function will process return of sliver status from node
    """
    pass

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
            'config': config[1], 'sliver_id': config[0]
            }
        return_data = ssh_connection(node.ipv6,
                                     username,
                                     settings.SERVER_PUBLIC_KEY,
                                     script)
        process_sliver_status(return_data)
    return True

def send_deploy_sliver(sliver):
    config = load_slice_config(sliver.slice)

    script = node_templates.SLICE_SCRIPT % {
        'config': config[1], 'slice_id': config[0]
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 username,
                                 settings.SERVER_PUBLIC_KEY,
                                 script)

def send_start_sliver(sliver):
    script = node_templates.SLIVER_START_SCRIPT % {
        'slice_id': "%.12i" % sliver.slice.id
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 username,
                                 settings.SERVER_PUBLIC_KEY,
                                 script)

def send_stop_sliver(sliver):
    script = node_templates.SLIVER_STOP_SCRIPT % {
        'slice_id': "%.12i" % sliver.slice.id
        }

    return_data = ssh_connection(sliver.node.ipv6,
                                 username,
                                 settings.SERVER_PUBLIC_KEY,
                                 script)

def ssh_connection(host, username, key, script):
    ssh = paramiko.SSHClient()
    nkey = paramiko.PKey(key)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = {}
    ssh.connect(host,
                username,
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
