from django.test import TestCase

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
