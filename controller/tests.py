from django.test import TestCase

from controller.utils import decode_version


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
