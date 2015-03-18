from django.core.exceptions import ValidationError


def validate_ifaces_nr(name, iface_cls, interfaces):
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
