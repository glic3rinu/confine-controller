"""
Tests for slices app using the unittest module.
These will pass when you run "manage.py test".
"""

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase

from users.models import Group, User

from .models import Slice, Sliver
from slices.exceptions import VlanAllocationError # use absolute import because
                                                  # of assertRaises!


class SliceTests(TestCase):
    fixtures = ['groups']
    
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
        Slice.objects.first().delete()
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
        User.objects.create_user(name='tech', username='tech',
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
