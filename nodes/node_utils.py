# -*- coding: utf-8 -*-
import socket

import node_templates

from slices import models as slice_models

def load_node_config(node):
    """
    Returns node config with all of its slices
    """
    slices = slice_models.Slice.objects.from_node(node.id)
    node_config = ""
    interfaces = ""
    ifnumber = 1
    for iface in list(node.interface_set.all()):
        interfaces += node_templates.INTERFACE_CONFIG_TEMPLATE % {
            'ifnumber': "%.2i" % ifnumber,
            'iftype': iface.type
            }
    for sl in slices:
        node_config += node_templates.NODE_CONFIG_TEMPLATE % {
            'sliver_id': "%.12i" % sl.id,
            'ssh_key': sl.user.get_profile().ssh_key,
            'fs_template_url': 'http://downloads.openwrt.org/backfire/10.03.1-rc6/x86_generic/openwrt-x86-generic-rootfs.tar.gz',
            'exp_data_url': 'http://distro.confine-project.eu/misc/openwrt-exp-data.tgz',
            'interfaces': interfaces
            }
        node_config += "\n\n"
    return node_config

def send_node_config(node):
    """
    Sends node configuration (all slices) to node platform
    """
    config = load_node_config(node)
    host = node.hostname
    port = node.port
    s = None
    error_message = ""
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOC_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error, msg:
            s = None
            error_message = msg
            continue
        try:
            s.connect(sa)
        except socket.error, msg:
            s.close()
            s = None
            error_message = msg
            continue
        break
    if s is None:
        return [False, error_message]
    s.sendall(config)
    return_data = s.recv(1024)
    s.close()
    return [True, return_data]

def extract_params(xml_tree, params = []):
    """
    Return a hast with extracted params from xml tree
    """
    return_hash = {}
    for param in params:
        return_hash[param] = xml_tree.find(param).text
    return return_hash
