"""
Tests for slices app using the unittest module.
These will pass when you run "manage.py test".
"""

import json

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase

from nodes.models import Node, DirectIface
from resources.models import Resource
from users.models import Group, User

# use absolute import because of assertRaises!
from slices.exceptions import VlanAllocationError
from .ifaces import IsolatedIface, Pub4Iface, Pub6Iface
from .models import Slice, Sliver


class SliceTests(TestCase):
    fixtures = ['groups', 'nodes', 'slices', 'slivers', 'templates']
    
    def test_bug623_data_fields_as_null(self):
        slice = Slice.objects.get(pk=3)
        self.assertIsNone(slice.sliver_defaults.data_uri)
        self.assertIsNone(slice.sliver_defaults.data_sha256)
        
        slice_url = reverse('slice-detail', args=(slice.pk,))
        response = self.client.get(slice_url)
        self.assertEqual(response.status_code, 200)
        try:
            slicejs = json.loads(response.content)
        except (TypeError, ValueError) as e:
            self.fail("Invalid response format: %s" % e)
        
        self.assertIsNone(slicejs['sliver_defaults']['data_uri'])
        self.assertIsNone(slicejs['sliver_defaults']['data_sha256'])
    
    def test_get_vlan_tag(self):
        # create slices with isolated_vlan_tag to use all vlan tags
        group = Group.objects.first()
        kwargs = dict(group=group, set_state=Slice.DEPLOY, allow_isolated=True)
        vlan_tags = range(Slice.MIN_VLAN_TAG, Slice.MAX_VLAN_TAG + 1)
        Slice.objects.bulk_create([
            Slice(name="Slice_%i" % tag, isolated_vlan_tag=tag, **kwargs) for tag in vlan_tags
        ])
        
        # should raise exception because no address space left
        self.assertRaises(VlanAllocationError, Slice._get_vlan_tag)
        
        # remove an object to release one address
        Slice.objects.filter(isolated_vlan_tag__isnull=False).first().delete()
        new_tag = Slice._get_vlan_tag()
        self.assertTrue(Slice.MIN_VLAN_TAG <= new_tag)
        self.assertTrue(Slice.MAX_VLAN_TAG >= new_tag)


class SliceTestCase(TestCase):
    fixtures = ['groups', 'slices', 'templates',]
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_unic_names(self):
        slice0 = Slice.objects.get(pk=1)
        slice1 = Slice.objects.get(pk=2)
        slice0.name = slice1.name
        self.assertRaises(IntegrityError, slice0.save)


class SliceViewsTestCase(TestCase):
    fixtures = ['groups', 'nodes', 'slices', 'slivers', 'templates']
    
    def setUp(self):
        User.objects.create_superuser(name='tech', username='tech',
                                 email='tech@localhost', password='tech')
        self.assertTrue(self.client.login(username='tech', password='tech'))
    
    def test_slice_changelist(self):
        changelist_url = reverse('admin:slices_slice_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
    
    def test_sliver_changelist(self):
        changelist_url = reverse('admin:slices_sliver_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)

    def test_sliver_changelist_all(self):
        # Show in changelist a sliver with multiple management interfaces
        changelist_url = reverse('admin:slices_sliver_changelist')
        response = self.client.get(changelist_url + '?my_slivers=False')
        self.assertEqual(response.status_code, 200)
    
    def test_sliver_changeview(self):
        # get sliver and its slice
        sliver = Sliver.objects.first()
        slice = sliver.slice
        
        # Update sliver to have set_state overrided
        sliver.set_state = Slice.START
        sliver.save()
        slice.set_state = Slice.REGISTER
        slice.save()
        
        # access via sliver default admin url
        sliver_change_url = reverse('admin:slices_sliver_change', args=(sliver.pk,))
        response = self.client.get(sliver_change_url)
        self.assertEqual(response.status_code, 200)
        
        # access via nested sliver admin url
        sliver_change_url = reverse('admin:slices_slice_slivers', args=(slice.pk, sliver.pk))
        response = self.client.get(sliver_change_url)
        self.assertEqual(response.status_code, 200)
    
    def test_add_sliver_view(self):
        slice = Slice.objects.get(pk=2)
        node = Node.objects.get(pk=2)
        self.assertFalse(Sliver.objects.filter(slice=slice, node=node))
        add_sliver_url = reverse('admin:slices_slice_add_sliver',
            kwargs={'slice_id': slice.pk, 'node_id': node.pk})
        
        response = self.client.get(add_sliver_url)
        self.assertEqual(response.status_code, 200)
    
    def test_incorrect_add_sliver_view(self):
        """
        Try to access to add_sliver_view with a combination
        of node and slice that alreday exists in a sliver.
        
        Controller should avoid that, because posting it
        should raise IntegrityError: duplicate key value
        violates unique constraint (slice_id, node_id)
        """
        sliver = Sliver.objects.first()
        slice = sliver.slice
        node = sliver.node
        self.assertTrue(Sliver.objects.filter(slice=slice, node=node))
        add_sliver_url = reverse('admin:slices_slice_add_sliver',
            kwargs={'slice_id': slice.pk, 'node_id': node.pk})
        
        response = self.client.get(add_sliver_url)
        self.assertEqual(response.status_code, 400)


class SliverIfacesTests(TestCase):
    fixtures = ['groups', 'nodes', 'slices', 'slivers', 'templates']
    
    def setUp(self):
        # Node with direct ifaces
        self.node_direct_iface = Node.objects.get(pk=1)
        self.assertTrue(self.node_direct_iface.direct_ifaces.exists())
        
        # Node without direct ifaces
        self.node_no_direct_iface = Node.objects.get(pk=2)
        self.assertFalse(self.node_no_direct_iface.direct_ifaces.exists())
        
        # Slice supports VLAN
        self.slice_vlan = Slice.objects.get(pk=1)
        self.assertTrue(self.slice_vlan.allow_isolated)
        
        # Slice doesn't support VLAN
        self.slice_no_vlan = Slice.objects.get(pk=2)
        self.assertFalse(self.slice_no_vlan.allow_isolated)
    
    def test_isolated_allowed(self):
        nodes = Node.objects.filter(pk=self.node_direct_iface.pk)
        slice = self.slice_vlan
        isolated = IsolatedIface()
        self.assertTrue(isolated.is_allowed(slice, nodes))
    
    def test_isolated_no_vlan(self):
        nodes = Node.objects.filter(pk=self.node_direct_iface.pk)
        slice = self.slice_no_vlan
        isolated = IsolatedIface()
        self.assertFalse(isolated.is_allowed(slice, nodes))
    
    def test_isolated_no_direct_ifaces(self):
        nodes = Node.objects.filter(pk=self.node_no_direct_iface.pk)
        slice = self.slice_vlan
        isolated = IsolatedIface()
        self.assertFalse(isolated.is_allowed(slice, nodes))
    
    def test_public4_allowed(self):
        node = self.node_direct_iface
        # create resource pub4 on the node
        node.resources.create(name='pub_ipv4', dflt_req=0, max_req=1)
        nodes = Node.objects.filter(pk=node.pk)
        slice = self.slice_vlan
        pub4 = Pub4Iface()
        self.assertTrue(pub4.is_allowed(slice, nodes))
    
    def test_public4_disallowed(self):
        node = self.node_direct_iface
        # check that the node doesn't have pub4 addresses
        self.assertFalse(node.resources.filter(name='pub_ipv4').exists())
        nodes = Node.objects.filter(pk=node.pk)
        slice = self.slice_vlan
        pub4 = Pub4Iface()
    
    def test_public6_allowed(self):
        node = self.node_direct_iface
        # create resource pub6 on the node
        node.resources.create(name='pub_ipv6', dflt_req=0, max_req=1)
        nodes = Node.objects.filter(pk=node.pk)
        slice = self.slice_vlan
        pub6 = Pub6Iface()
        self.assertTrue(pub6.is_allowed(slice, nodes))
    
    def test_public6_disallowed(self):
        node = self.node_direct_iface
        # check that the node doesn't have pub6 addresses
        self.assertFalse(node.resources.filter(name='pub_ipv6').exists())
        nodes = Node.objects.filter(pk=node.pk)
        slice = self.slice_vlan
        pub6 = Pub6Iface()
        self.assertFalse(pub6.is_allowed(slice, nodes))


class SliverTests(TestCase):
    fixtures = ['groups', 'nodes', 'slices', 'slivers', 'templates']
    
    def test_f450_sliver_without_mgmt_iface(self):
        sliver = Sliver.objects.get(pk=1)
        self.assertFalse(sliver.interfaces.filter(type='management').exists())
        
        sliver_url = reverse('sliver-detail', args=(sliver.pk,))
        response = self.client.get(sliver_url)
        self.assertEqual(response.status_code, 200)
        
        sliverjs = json.loads(response.content)
        self.assertIsNone(sliverjs['mgmt_net'])
    
    def test_f450_sliver_with_mgmt_iface(self):
        sliver = Sliver.objects.get(pk=2)
        mgmt_iface = sliver.interfaces.filter(type='management').first()
        self.assertIsNotNone(mgmt_iface)
        
        sliver_url = reverse('sliver-detail', args=(sliver.pk,))
        response = self.client.get(sliver_url)
        self.assertEqual(response.status_code, 200)
        
        sliverjs = json.loads(response.content)
        self.assertIsNotNone(sliverjs['mgmt_net'])
        self.assertEqual(sliverjs['mgmt_net']['addr'], str(mgmt_iface.ipv6_addr))
        self.assertEqual(sliverjs['mgmt_net']['backend'], 'native')

    def test_bug623_data_fields_as_null(self):
        sliver = Sliver.objects.get(pk=1)
        self.assertIsNone(sliver.data_uri)
        self.assertIsNone(sliver.data_sha256)
        
        sliver_url = reverse('sliver-detail', args=(sliver.pk,))
        response = self.client.get(sliver_url)
        self.assertEqual(response.status_code, 200)
        
        sliverjs = json.loads(response.content)
        self.assertIsNone(sliverjs['data_uri'])
        self.assertIsNone(sliverjs['data_sha256'])


class HelpersTests(TestCase):
    def test_is_valid_description(self):
        from .helpers import is_valid_description
        self.assertFalse(is_valid_description(""))
        self.assertFalse(is_valid_description("Too few words."))
        self.assertFalse(is_valid_description("fooooooooooooooooooooooooooooooo."))
        self.assertTrue(is_valid_description("This is an experiment to check "
                                             "network speed."))
