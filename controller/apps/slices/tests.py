"""
Tests for slices app using the unittest module.
These will pass when you run "manage.py test".
"""

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import TestCase

from users.models import User
from slices.models import Slice, Sliver, Template


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
        user = User.objects.create_user(name='tech', username='tech',
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
