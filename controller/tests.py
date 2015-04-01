from django.core.exceptions import ValidationError
from django.test import TestCase

from controller.core.validators import (validate_net_iface_name_with_vlan,
    validate_ssh_pubkey)
from controller.utils import decode_version

from users.models import User


class AuthenticatedTestCase(TestCase):
    """Test case with several user roles authentication."""
    fixtures = ['groups.json', 'users.json', 'roles.json']

    class Meta:
        abstract = True

    def setUp(self):
        """
        By default the tests are executed as unprivileged user
        """
        # Update the passwords to be usable during testing
        # because fixture and test can have different PASSWORD_HASHERS
        for user in User.objects.all():
            user.set_password("%spass" % user.username)
            user.save()

        self._login()

    def _login(self, superuser=False, admin=False, tech=False):
        if superuser:
            user = 'super'
        elif admin:
            user = 'admin'
        elif tech:
            user = 'tech'
        else:
            user = 'user'
        return self.login(user)
    
    def login(self, user='user'):
        """Login a user into the system."""
        self.client.logout()
        if user not in ['super', 'admin', 'tech', 'researcher', 'user']:
            raise ValueError('Invalid value for user: "%s"' % user)
        
        pwd = "%spass" % user
        res = self.client.login(username=user, password=pwd)
        self.assertTrue(res, "Logging in user %s, pwd %s failed." % (user, pwd))


class ControllerTests(TestCase):
    def test_decode_version(self):
        self.assertEqual(decode_version('0.12'), (0, 12, 0))
        self.assertEqual(decode_version('0.12.3'), (0, 12, 3))
        self.assertEqual(decode_version('0.12.3a4'), (0, 12, 3))
        self.assertEqual(decode_version('0.12.3b5'), (0, 12, 3))
        self.assertEqual(decode_version('0.12.3rc6'), (0, 12, 3))
        self.assertEqual(decode_version('1.0'), (1, 0, 0))
        self.assertEqual(decode_version('1.0b3'), (1, 0, 0))
        self.assertRaises(ValueError, decode_version, '0_34b')
        self.assertRaises(ValueError, decode_version, '=0.34b')
        self.assertRaises(TypeError, decode_version, None)
        self.assertRaises(TypeError, decode_version, 0123)


class ValidatorsTests(TestCase):
    def test_validate_net_iface_name_with_vlan(self):
        # http://wiki.openwrt.org/doc/networking/network.interfaces
        validate_net_iface_name_with_vlan('eth')
        validate_net_iface_name_with_vlan('eth0')
        validate_net_iface_name_with_vlan('eth0.10')
        validate_net_iface_name_with_vlan('wlan1')
        validate_net_iface_name_with_vlan('wlan.0')
        validate_net_iface_name_with_vlan('wlan1.20')
        validate_net_iface_name_with_vlan('WLAN')
        self.assertRaises(ValidationError, validate_net_iface_name_with_vlan, '0eth')
        self.assertRaises(ValidationError, validate_net_iface_name_with_vlan, 'eth1.01')
    
    def test_validate_ssh_pubkey(self):
        pubkey = ('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsHDcbPXptz4i6iz2EGif'
                  'D8JZ3acFnR6FG6aPDQxmoESLjNw6n6MoVOkeXvs+Phgra30dQLnLa23pFCb'
                  'vYxrX5HY370Dtx2981uz0RFws+85pBviIIsdnma/Wzz05PDhTb3vnTGUOp+'
                  'xOKRl6xptiESbz+Jgi1ImCkx85rBCWj9jQQNi0hddkBi41F/UzMLorWGICa'
                  'yC/wGvg7JDnYhlKv+HXSYoylQvnrY/891mR6BNBYU+N1506VndHLz0VDWii'
                  'bxwM2vkpy6h+/dt2OLsMXzuDSSUpqYynwYXPC6PaCzzrv18qBTUzT9dof0x'
                  'o6Nib+clykex/C7FnIaFD4HW9N')
        pubkey_with_comment = pubkey + ' confine@confine'
        validate_ssh_pubkey(pubkey)
        validate_ssh_pubkey(pubkey_with_comment)
        self.assertRaises(ValidationError, validate_ssh_pubkey, 'ssh-rsa FooPubKey')
