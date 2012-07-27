
UPLOAD_NODE_DATA = '<?xml version="1.0" encoding="utf-8"?><node version="1.0"><hostname>host1</hostname><ip>1.1.1.1</ip><architecture>x86_generic</architecture></node>'

HOSTNAME_NODE_DATA = '<?xml version="1.0" encoding="utf-8"?><node version="1.0"><id>%i</id></node>'

NODE_CREATION = {
    'hostname': 'hostname',
    'ip': '1.1.1.1',
    'rd_arch': 'x86_generic',
    'admin': None,
    'rd_uuid': 'uuid',
    'rd_pubkey': 'PUBKEY',
    'rd_cert': 'RDCERT',
    'rd_boot_sn': 1,
    'nodeprops': [
        {
            'name': 'NAME',
            'value': 'VALUE'
            }
        ]
    }
