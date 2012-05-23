
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
\toption if00_type       internal
%(interfaces)s
EOF
"""

INTERFACE_CONFIG_TEMPLATE = "\toption if%(ifnumber)s_type       %(iftype)s\n"
