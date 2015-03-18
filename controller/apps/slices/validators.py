from django.core.exceptions import ValidationError


def validate_ifaces_nr(name, iface_cls, interfaces):
    """Validate nr depending on interface type."""
    if not hasattr(iface_cls, 'NR_MAIN_IFACE'):
        return
    
    valid_nr_main_iface = True
    for iface in interfaces:
        if iface.type == name:
            if iface.nr == iface_cls.NR_MAIN_IFACE:
                return
            valid_nr_main_iface = False
    
    if not valid_nr_main_iface:
        raise ValidationError('nr should be %i for the main %s interface.' %
                              (iface_cls.NR_MAIN_IFACE, name))


def validate_private_iface(interfaces):
    """Check that mandatory private interface has been defined."""
    priv_ifaces = 0
    for iface in interfaces:
        if iface.type == 'private':
            priv_ifaces += 1
        if priv_ifaces > 1:
            raise ValidationError('There can only be one interface of type private.')
    if priv_ifaces == 0:
        raise ValidationError('There must exist one interface of type private.')
