from django.core.exceptions import ValidationError


def sliver_mac_prefix_validator(value):
    # TODO also limit to 16 bits
    try: int(value, 16)
    except: ValidationError('%s is not a hex value.' % value)
