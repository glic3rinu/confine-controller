from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase

from users.models import Group, User
from .models import Island, Node


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
