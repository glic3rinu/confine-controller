import json

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from users.models import Group, User
from .models import Island, Node, Server, ServerApi


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
