"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.exceptions import SuspiciousFileOperation
from django.core.management import call_command
from django.test import TestCase

from nodes.models import Node, Server, ServerApi
from pki import ca
from users.models import Group

from .models import BaseImage, Build, Config, ConfigPlugin
from .plugins.authkeys import AuthKeysPlugin
from .plugins.password import PasswordPlugin
from .plugins.usbimage import USBImagePlugin
from .serializers import NodeFirmwareConfigSerializer
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


class AuthKeysPluginTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='group', allow_nodes=True)
        self.node = Node.objects.create(name='node', group=self.group, arch='i686')
        plugin = AuthKeysPlugin()
        self.serializer_class = plugin.get_serializer()
    
    def test_serializer_valid(self):
        data = {
            "allow_node_admins": True,
            "ssh_auth": "",
            "sync_node_admins": False,
        }
        serializer = self.serializer_class(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_serializer_valid_no_data(self):
        data = {}
        serializer = self.serializer_class(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_serializer_invalid_ssh_key(self):
        # invalid ssh key
        data = {
            "allow_node_admins": True,
            "ssh_auth": "foo_ssh_key",
            "sync_node_admins": False,
        }
        serializer = self.serializer_class(self.node, data=data)
        self.assertFalse(serializer.is_valid())


class PasswordPluginTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='group', allow_nodes=True)
        self.node = Node.objects.create(name='node', group=self.group, arch='i686')
        plugin = PasswordPlugin()
        self.serializer_class = plugin.get_serializer()
    
    def test_serializer_valid(self):
        data = {'password': 'secret'}
        serializer = self.serializer_class(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_serializer_valid_disable(self):
        data = {'disable_password': True}
        serializer = self.serializer_class(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertFalse(serializer.data['password'])
    
    def test_serializer_valid_no_data(self):
        data = {}
        serializer = self.serializer_class(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertFalse(serializer.data['password'])
    
    def test_serializer_invalid_no_password_but_enabled(self):
        data = {
            'disable_password': False,
            'password': '',
        }
        serializer = self.serializer_class(self.node, data=data)
        self.assertFalse(serializer.is_valid())


class USBImagePluginTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='group', allow_nodes=True)
        self.node = Node.objects.create(name='node', group=self.group, arch='i686')
        plugin = USBImagePlugin()
        self.serializer_class = plugin.get_serializer()
    
    def test_serializer_valid_no_data(self):
        data = {}
        serializer = self.serializer_class(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertFalse(serializer.data['usb_image'])


class NodeFirmwareConfigTests(TestCase):
    def setUp(self):
        # FirmwareConfig --> migration firmware/0034
        config = Config.objects.get()
       
        # BaseImage for i686 nodes
        self.base_image = BaseImage.objects.create(name='bi', config=config,
                                                   architectures=['i686'])
        
        # ServerApi --> migration nodes/0013 + configure server cert
        self.assertTrue(ServerApi.objects.filter(type='registry').exists())
        call_command('setuppki', verbosity=0, interactive=False)
        server = Server.objects.get_default()
        server.api.filter(base_uri__contains=server.mgmt_net.addr).update(
            cert=ca.get_cert().as_pem()
        )
        
        # Node
        self.group = Group.objects.create(name='group', allow_nodes=True)
        self.node = Node.objects.create(name='node', group=self.group, arch='i686')
    
    def test_valid_no_data(self):
        serializer = NodeFirmwareConfigSerializer(self.node, data={})
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_valid_no_base_image(self):
        data = {
            "registry_base_uri": "http://[fd65:fc41:c50f::2]/api/",
            "registry_cert": ""
        }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_valid_http(self):
        data = {
            "base_image_id": self.base_image.pk,
            "registry_base_uri": "http://[fd65:fc41:c50f::2]/api/",
            "registry_cert": ""
        }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_valid_https(self):
        data = {
            "base_image_id": self.base_image.pk,
            "registry_base_uri": "https://[fd65:fc41:c50f::2]/api/",
            "registry_cert": (
                "-----BEGIN CERTIFICATE-----\n"
                "MIICxjCCAa6gAwIBAwIEOutGXzANBgkqhkiG9w0BAQsFADAcMRowGAYDVQQDExFm\n"
                "ZDY1OmZjNDE6YzUwZjo6MjAeFw0xNDA0MDgwOTEyMzdaFw0xODA0MDcwOTEyMzda\n"
                "MBwxGjAYBgNVBAMTEWZkNjU6ZmM0MTpjNTBmOjoyMIIBIjANBgkqhkiG9w0BAQEF\n"
                "AAOCAQ8AMIIBCgKCAQEAqDCfwaYC2mtCksS1ER22fZWM5UJdkDlMoTiSmG2sLgxA\n"
                "hvnD7koocrsxi1MEZkTEnbDJPzAH+hLGMUyveMDZ/yBhYCvfMJOO+J36Dplyi4EG\n"
                "zfM1QwATZxuTAOzAzZW8FbIhQ6ExQJPvKjpir6FhfXglKbZm8iP7u3V6twFHAtiE\n"
                "a4AkMNEkgHjmvLfB+G4wE+k/WEHU4HH/EZmMF9y8Zq8Wku+PrUql034MYlnHqkzh\n"
                "QTK9UJGrTyT5hjp6a8XOz6J7zPhLG0Y7vIir/9NeIKVYCUVPstQhMqBWaA48gM+r\n"
                "umqMp3YDamUs6XxI9FVk5x24o5WUungyjw0N3nLb3QIDAQABoxAwDjAMBgNVHRME\n"
                "BTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCJdgEX9Gc7/NWsj0sLqfPAdLw+c40W\n"
                "Ff17ftW3ok3V27HFLi6HAk5gL4LO4pCxt7emMpxmMxyLETmSAkDZ7mgv3T2Vg1cc\n"
                "XRsJhX/h3LBcV68TVCKsnEYzf7FqBfcQmE1ZQQ1F72+ITwrARDEgnD2pyZQ0olCx\n"
                "1z2XatQykneg9GpJQhZAlIfFT8ke7TWDzIkx808498wMBdUnork6piUO6KGOsJ9O\n"
                "NCHdn/ThGxv9CPCcBJ7asHdD9HkQT2IPKoRnA7KKMXZx84bn5qI7pr79BfAHvw/T\n"
                "+k+vlEz1nSrreue3bv1Aq17ZlIB6IQga11hLaHqkT6hSkoBJwpUhsY6C\n"
                "-----END CERTIFICATE-----")
         }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_valid_tinc_default_gateway(self):
        # check if default server exists
        dflt_server = Server.objects.first()
        self.assertIsNotNone(dflt_server)
        
        # check if server's tinc configuration has been initialized
        gateway = dflt_server.related_tinc.first()
        self.assertIsNotNone(gateway)
        
        # create an address for tinc
        gateway.addresses.create(addr='1.0.0.1')
        
        data = {"tinc_default_gateway": gateway.name}
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(self.node.tinc.default_connect_to, gateway)
    
    def test_invalid_tinc_default_gateway_does_not_exist(self):
        data = {"tinc_default_gateway": "invalid_gateway"}
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_tinc_default_gateway_no_addresses(self):
        gateway = self.node.tinc
        self.assertFalse(gateway.addresses.exists())
        data = {"tinc_default_gateway": gateway.name}
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_https_without_cert(self):
        data = {
            "base_image_id": self.base_image.pk,
            "registry_base_uri": "https://[fd65:fc41:c50f::2]/api/",
            "registry_cert": ""
        }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_base_image_not_available(self):
        data = { "base_image_id": -1 }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_base_image_id(self):
        data = { "base_image_id": "invalid_ID" }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_registry_base_uri(self):
        data = { "registry_base_uri": "foo:/malformed" }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_registry_cert(self):
        data = { "registry_cert": "--FOO CERT--"}
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_cert_but_not_registry_base_uri(self):
        # only cert but not base_uri
        data = {
            "registry_cert": (
                "-----BEGIN CERTIFICATE-----\n"
                "MIICxjCCAa6gAwIBAwIEOutGXzANBgkqhkiG9w0BAQsFADAcMRowGAYDVQQDExFm\n"
                "ZDY1OmZjNDE6YzUwZjo6MjAeFw0xNDA0MDgwOTEyMzdaFw0xODA0MDcwOTEyMzda\n"
                "MBwxGjAYBgNVBAMTEWZkNjU6ZmM0MTpjNTBmOjoyMIIBIjANBgkqhkiG9w0BAQEF\n"
                "AAOCAQ8AMIIBCgKCAQEAqDCfwaYC2mtCksS1ER22fZWM5UJdkDlMoTiSmG2sLgxA\n"
                "hvnD7koocrsxi1MEZkTEnbDJPzAH+hLGMUyveMDZ/yBhYCvfMJOO+J36Dplyi4EG\n"
                "zfM1QwATZxuTAOzAzZW8FbIhQ6ExQJPvKjpir6FhfXglKbZm8iP7u3V6twFHAtiE\n"
                "a4AkMNEkgHjmvLfB+G4wE+k/WEHU4HH/EZmMF9y8Zq8Wku+PrUql034MYlnHqkzh\n"
                "QTK9UJGrTyT5hjp6a8XOz6J7zPhLG0Y7vIir/9NeIKVYCUVPstQhMqBWaA48gM+r\n"
                "umqMp3YDamUs6XxI9FVk5x24o5WUungyjw0N3nLb3QIDAQABoxAwDjAMBgNVHRME\n"
                "BTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCJdgEX9Gc7/NWsj0sLqfPAdLw+c40W\n"
                "Ff17ftW3ok3V27HFLi6HAk5gL4LO4pCxt7emMpxmMxyLETmSAkDZ7mgv3T2Vg1cc\n"
                "XRsJhX/h3LBcV68TVCKsnEYzf7FqBfcQmE1ZQQ1F72+ITwrARDEgnD2pyZQ0olCx\n"
                "1z2XatQykneg9GpJQhZAlIfFT8ke7TWDzIkx808498wMBdUnork6piUO6KGOsJ9O\n"
                "NCHdn/ThGxv9CPCcBJ7asHdD9HkQT2IPKoRnA7KKMXZx84bn5qI7pr79BfAHvw/T\n"
                "+k+vlEz1nSrreue3bv1Aq17ZlIB6IQga11hLaHqkT6hSkoBJwpUhsY6C\n"
                "-----END CERTIFICATE-----")
        }
        serializer = NodeFirmwareConfigSerializer(self.node, data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_invalid_unsupported_node_arch(self):
        # Build firmware node with arch incompatible (no base images)
        node_x64 = Node.objects.create(name='Node_x64', group=self.group, arch='x64')
        serializer = NodeFirmwareConfigSerializer(node_x64, data={})
        self.assertFalse(serializer.is_valid())
