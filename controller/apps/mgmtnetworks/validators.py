from django.core.exceptions import ValidationError
from IPy import IP
from M2Crypto import X509


def validate_csr(csr, addr):
    """ Validate Certificate Signing Request (CSR) """
    try:
        csr = X509.load_request_string(str(csr))
    except:
        raise ValidationError('Not a valid CSR')
    subject = csr.get_subject()
    if not subject.CN:
        raise ValidationError("Required subject Common Name (CN) not provided")
    try:
        cnip = IP(subject.CN)
    except ValueError:
        msg = "Subject Common Name (CN) '%s' is not a valid IP address"
        raise ValidationError(msg % subject.CN)
    if addr != cnip:
        msg = "Common Name (CN) must be equal to node management address: '%s' != '%s'"
        raise ValidationError(msg % (subject.CN, addr))
