# -*- coding: utf-8 -*-

#option if01_type       %(if01_type)s   
#option if01_ipv4_proto %(if01_ipv4_proto)s
#option if02_type       %(if02_type)s
#option if01_parent     %(if01_parent)s

NODE_CONFIG_TEMPLATE = """
confine_sliver_allocate <<EOF
config sliver %(sliver_id)s
\toption user_pubkey     '%(ssh_key)s'
\toption fs_template_url '%(fs_template_url)s'
\toption exp_data_url    '%(exp_data_url)s'
%(interfaces)s
EOF
"""


SLIVER_INTERFACE_TYPE = "\toption if%(number)s_type '%(type)s'\n"
SLIVER_INTERFACE_NAME = "\toption if%(number)s_name '%(name)s'\n"
SLIVER_INTERFACE_IPV4_PROTO = "\toption if%(number)s_ipv4_proto '%(proto)s'\n"
SLIVER_INTERFACE_IPV4 = "\toption if%(number)s_ipv4 '%(ip)s'\n"
SLIVER_INTERFACE_IPV6_PROTO = "\toption if%(number)s_ipv6_proto '%(proto)s'\n"
SLIVER_INTERFACE_IPV6 = "\toption if%(number)s_ipv6 '%(ip)s'\n"
SLIVER_INTERFACE_MAC = "\toption if%(number)s_mac '%(mac)s'\n"

SLIVER_SCRIPT = """
#!/bin/bash
confine_sliver_allocate %(sliver_id)s << EOF 
%(config)s
EOF
"""

SLICE_SCRIPT = """
#!/bin/bash
confine_sliver_deploy %(slice_id)s <<EOF
%(config)s
EOF
"""

SLIVER_START_SCRIPT = """
#!/bin/bash
confine_sliver_start %(slice_id)s <<EOF
EOF
"""

SLIVER_STOP_SCRIPT = """
#!/bin/bash
confine_sliver_stop %(slice_id)s <<EOF
EOF
"""
