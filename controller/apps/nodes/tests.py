import json
import unittest

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from users.models import Group, User
from .models import Island, Node, NodeApi, Server, ServerApi


class IslandTest(TestCase):
    def setUp(self):
        self.password = 'vct'
        self.user = User.objects.create_superuser(username='vct', name='vct',
            email='vct@localhost', password=self.password)
        self.client.login(username=self.user.username, password=self.password)
    
    def test_changeview(self):
        # Test island changeview (regression on #157 rev 1974935d)
        island = Island.objects.create(name='Island', description='Island to test changeview.')
        island_url = reverse('admin:nodes_island_change', args=(island.pk,))
        resp = self.client.get(island_url)
        self.assertTrue(200, resp.status_code)


class NodeTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='group', allow_nodes=True)
        admin = User.objects.create_user(username='admin', name='admin',
            email='admin@localhost', password='admin')
        self.group.roles.create(user=admin, is_group_admin=True)
    
    def test_sliver_pub_ipv4(self):
        """Check proper validation of Node.sliver_pub_ipv4 (#391)"""
        node = Node.objects.create(name='node', group=self.group)
        node.sliver_pub_ipv4 = 'auto' # invalid choice
        # model.save() doesn't call validation methods, use full_clean instead
        self.assertRaises(ValidationError, node.full_clean)
        
        # invalid range configuration
        node.sliver_pub_ipv4 = Node.RANGE
        self.assertRaises(ValidationError, node.full_clean)
        
        # valid range configuration
        node.sliver_pub_ipv4_range = '10.0.0.1#8'
        node.full_clean()
        
        # invalid dhcp configuration
        node.sliver_pub_ipv4 = Node.DHCP
        node.sliver_pub_ipv4_range = '#invalid'
        self.assertRaises(ValidationError, node.full_clean)
        
        # valid dhcp configuration
        node.sliver_pub_ipv4_range = '#3'
        node.full_clean()
    
    def test_api_duplicate_cert(self):
        # Can exists node APIs with duplicate certificates
        # e.g. two nodes delegate their API to a proxy server
        uri = 'https://foo_proxy.local'
        cert = """
               -----BEGIN CERTIFICATE-----
               MIIC6jCCAdKgAwIBAwIEUBs03jANBgkqhkiG9w0BAQsFADAcMRowGAYDVQQDExFm
               ZDY1OmZjNDE6YzUwZjo6MjAeFw0xNDExMjcxNDA5NDBaFw0xODExMjYxNDA5NDBa
               MFIxMDAuBgkqhkiG9w0BCQEWIWdyb3VwYWRtaW4xNDE3MDk3MzczMTcwQGxvY2Fs
               aG9zdDEeMBwGA1UEAxMVZmQ2NTpmYzQxOmM1MGY6NTdlOjoyMIIBIjANBgkqhkiG
               9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0RuoerrwIzbmqDaP1E6ZQ8YI6ctWGicUWlvT
               mXxdSnr/9zzO1lT23zylJoJiBBTtFTNnUbmlcQeHlWYX+sS/N/ztqpiuEGZzrUL4
               fDrfrLtcqjxOaY8VwNCK/Zxh562rgdcvNyKvs/4KD8uvBqHVFeA6wfoFu+N9zOfJ
               /5zTBFV+ZM1iHRyvCgo14If/MsjFVso7BTpTGkRA9VXRVHXgNP3eI+cZ34xtNoXd
               /DKCIg+sko+EbENCMTxwKzeJeBA0Dalo6O/52O/WHxP14kqcvDFlN4eprrK6MnrF
               qQ9xmfkmRRQSL2AuJKvUX+Nj7N8LyfZ+3q6bttkRWd+AdvxTTQIDAQABMA0GCSqG
               SIb3DQEBCwUAA4IBAQAqhd7NVUBex/J7/c73exdjan/RLY9C3h4Kh+Vvz3HRkxSY
               YiC2IeC+oiS/o2m8hA5J+B3Alnkuu8QRyE9Xz0W8/sUPEHsZShPdZz68aHt2oMOg
               Lkkkx8xYlX7p4bkJzM0A5kZ3zNdq0AsgCePLeV0DLexhLDQZo9uHahL9byNGVKxH
               bEZfhECmKZSvxn0zOsToxVJrUSemBrUa93YW97zpLHlgA5WQn6ccz489i2Q/9qVZ
               ZU7FnHfMSuOasG8JPgC1IgeYAYBuLXP/gUMapU+9OxaaCjjDFJGnMupfmn2Endss
               g+avz/mFfePLGvtjJosQLNN2dKobEm+Lgautgt5s
               -----END CERTIFICATE-----
               """
        node_one = Node.objects.create(name='one', group=self.group)
        node_two = Node.objects.create(name='two', group=self.group)
        NodeApi.objects.create(node=node_one, cert=cert, base_uri=uri)
        NodeApi.objects.create(node=node_two, cert=cert, base_uri=uri)
        self.assertEqual(node_one.api.cert, cert)
        self.assertEqual(node_two.api.cert, cert)
    
    def test_generate_certificate_node_api_none(self):
        # Fw generator should create a default api with its certificate
        node = Node.objects.create(name='node', group=self.group)
        key = node.tinc.generate_key(commit=True)
        self.assertFalse(NodeApi.objects.filter(node=node).exists())
        
        cert = node.generate_certificate(key, commit=True)
        
        self.assertTrue(NodeApi.objects.filter(node=node).exists())
        self.assertIn(str(node.mgmt_net.addr), node.api.base_uri)
        self.assertEqual(node.api.cert, cert)
    
    def test_generate_certificate_node_api_mgmt_net(self):
        # Fw generator should generate and store api certificate
        node = Node.objects.create(name='node', group=self.group)
        key = node.tinc.generate_key(commit=True)
        NodeApi.objects.create_default(node)
        
        cert = node.generate_certificate(key, commit=True)
        self.assertIn(str(node.mgmt_net.addr), node.api.base_uri)
        self.assertEqual(node.api.cert, cert)
    
    def test_generate_certificate_node_api_proxy_delegated(self):
        # Fw generator should keep current node api certificate
        node = Node.objects.create(name='node', group=self.group)
        proxy_key = node.tinc.generate_key(commit=False)
        proxy_cert = node.generate_certificate(proxy_key, commit=False)
        NodeApi.objects.create(node=node, base_uri='https://proxy', cert=proxy_cert)
        
        key = node.tinc.generate_key(commit=True)
        cert = node.generate_certificate(key, commit=True)
        
        self.assertIsNotNone(node.api.base_uri)
        self.assertEqual(node.api.cert, proxy_cert, "Customized certificate overrided!")


class ServerTest(TestCase):
    def setUp(self):
        super(ServerTest, self).setUp()
        self.island = Island.objects.create(name="RandomIsland")
        self.server = Server.objects.create(description="A server")
        self.server_api = ServerApi.objects.create(type=ServerApi.REGISTRY,
            server=self.server, island=self.island)
    
    def test_delete_behaviour(self):
        # Check deletion behaviour #487
        self.island.delete()
        try:
            server_api = ServerApi.objects.get(pk=self.server_api.pk)
        except ServerApi.DoesNotExist:
            self.fail("ServerApi has been removed!")
        self.assertIsNone(server_api.island)
    
    def test_registry_api_view(self):
        # Test registry api vew used by firmware build form
        # to load via AJAX the base_uri and cert data
        url = reverse('admin:nodes_server_api')
        
        # invalid request withouth data
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        
        # invalid request with invalid data
        resp = self.client.get(url + '?id=bad')
        self.assertEqual(resp.status_code, 404)
        
        # valid request
        resp = self.client.get(url + '?id=%s' % self.server_api.pk)
        self.assertEqual(resp.status_code, 200)
        try:
            apijs = json.loads(resp.content)
        except ValueError:
            self.fail("Response should be JSON serialized data.")
        self.assertIn('base_uri', apijs)
        self.assertIn('cert', apijs)
        self.assertEqual(apijs['base_uri'], self.server_api.base_uri)
        self.assertEqual(apijs['cert'], self.server_api.cert)
    
    def test_delete_unique_server(self):
        if not Server.objects.exists():
            raise unittest.SkipTest("At least one server should exist.")
        # try to delete all queryset
        self.assertRaises(PermissionDenied, Server.objects.all().delete)
        
        # try to delete server instance
        server = Server.objects.get_default()
        Server.objects.exclude(pk=server.pk).delete()
        self.assertRaises(PermissionDenied, server.delete)
