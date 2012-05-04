NODE_CONFIG_TEMPLATE = """
confine_sliver_allocate <<EOF
config sliver %(sliver_id)s
    option user_pubkey     '%(ssh_key)s'
    option fs_template_url '%(fs_template_url)s'
    option exp_data_url    '%(exp_data_url)s'
    option if00_type       %(if00_type)s 
    option if01_type       %(if01_type)s   
    option if01_ipv4_proto %(if01_ipv4_proto)s
    option if02_type       %(if02_type)s
    option if01_parent     %(if01_parent)s
EOF
"""
