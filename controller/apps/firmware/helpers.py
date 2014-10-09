import tempfile
from controller.utils.system import run


def pem2der_string(pem_string):
    """
    Converts private key or certificate from ascii-armored
    PEM format to binary DER format.
    Based on openssl as described in OpenWrt Wiki:
    http://wiki.openwrt.org/doc/howto/certificates.overview
    
    """
    # FIXME: temporal files can be avoid using load_cert_string?
    # write PEM content to a temporal file
    pem_file = tempfile.NamedTemporaryFile()
    pem_file.write(pem_string)
    pem_file.seek(0)
    
    # use another temporal file to write binary DER
    der_file = tempfile.NamedTemporaryFile()
    
    if 'CERTIFICATE' in pem_string:
        run('openssl x509 -in %s -outform DER -out %s' % (pem_file.name, der_file.name))
    elif 'RSA PRIVATE KEY' in pem_string:
        run('openssl rsa -in %s -outform DER -out %s' % (pem_file.name, der_file.name))
    else:
        raise ValueError('Invalid literal for pem2der_string provided.')
    return der_file.read()
