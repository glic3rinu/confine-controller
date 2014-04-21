"""
Tests for slices app using the unittest module.
These will pass when you run "manage.py test".
"""

from django.db import IntegrityError
from django.test import TestCase

from users.models import Group
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

class SlicesViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/admin/slices/')
        self.assertEqual(resp.status_code, 200)
