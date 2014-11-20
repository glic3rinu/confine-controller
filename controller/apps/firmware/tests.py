"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.exceptions import SuspiciousFileOperation
from django.core.management import call_command
from django.test import TestCase

from nodes.models import Node
from users.models import Group

from .models import Build, ConfigPlugin
from .settings import FIRMWARE_BUILD_IMAGE_STORAGE

class BuildTests(TestCase):
    def test_handle_access_denied_image_file(self):
        group = Group.objects.create(name='group', allow_nodes=True)
        node = Node.objects.create(name='node', group=group)
        build = Build.objects.create(node=node, task_id='926ec44c-4842-417b-a45d-4b7c858888cf')
        # Point image outside of FIRMWARE_BUILD_IMAGE_STORAGE
        build.image.name = FIRMWARE_BUILD_IMAGE_STORAGE.location + '../image.tgz'
        try:
            build.state
        except SuspiciousFileOperation:
            self.failureException
    
    def test_kwargs_dict(self):
        b = Build(kwargs="{'registry_cert': u'', 'usb_image': False}")
        self.assertIsInstance(b.kwargs_dict, dict)
        self.assertEqual(['registry_cert', 'usb_image'], b.kwargs_dict.keys())
        self.assertEqual(b.kwargs_dict['registry_cert'], u'')
        self.assertFalse(b.kwargs_dict['usb_image'])
    
    def test_invalid_kwargs_dict(self):
        # can handle invalid kwargs format?
        b = Build(kwargs=u'')
        self.assertIsInstance(b.kwargs_dict, dict)
        
        b.kwargs = None
        self.assertIsInstance(b.kwargs_dict, dict)
        
        b.kwargs = "{'malformed_dict':}"
        self.assertIsInstance(b.kwargs_dict, dict)


class PluginTests(TestCase):
    def test_enabled_by_default(self):
        plugins = ConfigPlugin.objects
        # database is clean so there is no plugins yet
        self.assertEqual(plugins.count(), 0)
        
        # synchronize firmware plugins
        call_command('syncfirmwareplugins')
        
        # check that all plugins has been initialized
        # and USBImage and AuthKeys are enabled
        self.assertEqual(plugins.count(), 3)
        enabled = plugins.filter(is_active=True).values_list('label', flat=True)
        self.assertIn('USBImagePlugin', enabled)
        self.assertIn('AuthKeysPlugin', enabled)
