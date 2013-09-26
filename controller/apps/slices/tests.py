"""
Tests for slices app using the unittest module.
These will pass when you run "manage.py test".
"""

from django.db import IntegrityError
from django.test import TestCase

from slices.models import Slice, Sliver, Template


class SliceTestCase(TestCase):
#    fixtures = ['slices', 'nodes',]
    def setUp(self):
        'Populate test database with model instances'
        template = Template(name="template0", image="image.tar.gz")
        template.save()

        self.slice0 = Slice(name="slice0", template=template)
        self.slice1 = Slice(name="slice1", template=template)
        self.slice0.save()
        self.slice1.save()

#        node = Node.objects.get()
#        slv = Sliver()

    def tearDown(self):
        for model in [Slice, Sliver, Template]:
            for obj in model.objects.all():
                obj.delete()

    def test_unic_names(self):
        self.slice0.name = "slice1"
        self.assertRaises(IntegrityError, self.slice0.save)
#        pass

class SlicesViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/admin/slices/')
        self.assertEqual(resp.status_code, 200)
