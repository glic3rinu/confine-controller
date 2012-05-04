# -*- coding: utf-8 -*-
import socket

from node_templates import NODE_CONFIG_TEMPLATE

from slices import models as slice_models

def load_node_config(node):
    """
    Returns node config with all of its slices
    """
    slices = slice_models.Slice.objects.from_node(node.id)
    node_config = ""
    for sl in slices:
        node_config += NODE_CONFIG_TEMPLATE % {
            'sliver_id': "%.12i" % sl.id,
            'ssh_key': sl.user.ssh_key,
            'fs_template_url': 'http://downloads.openwrt.org/backfire/10.03.1-rc6/x86_generic/openwrt-x86-generic-rootfs.tar.gz',
            'exp_data_url': 'http://distro.confine-project.eu/misc/openwrt-exp-data.tgz',
            'if00_type': 'internal',
            'if01_type': 'public',
            'if01_ipv4_proto': 'static',
            'if02_type': 'isolated',
            'if01_parent': 'eth1',
            }
        node_config += "\n\n"
    return node_config

def send_node_config(node):
    """
    Sends node configuration (all slices) to node platform
    """
    config = load_node_config(node)
    node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node_socket.connect((node.ip, node.port))
    node_socket.sendall(config)
    data = node_socket.recv(1024)
    node_socket.close()
    return data

def extract_params(xml_tree, params = []):
    """
    Return a hast with extracted params from xml tree
    """
    return_hash = {}
    for param in params:
        return_hash[param] = xml_tree.find(param).text
    return return_hash
