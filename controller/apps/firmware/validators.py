from controller.core.validators import validate_ssh_pubkey


def validate_ssh_auth(value):
    """Validate SSH Public Keys but allow comments."""
    value = value.strip()
    for ssh_pubkey in value.splitlines():
        if not ssh_pubkey.lstrip().startswith('#'): # ignore comments
            validate_ssh_pubkey(ssh_pubkey)
    return value
