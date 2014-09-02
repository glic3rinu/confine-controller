"""
Test controller api app.
"""
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from nodes.models import Node
from slices.models import Sliver


class FilteringTests(TestCase):
    fixtures = ['groups.json', 'nodes.json', 'slices.json', 'slivers.json',
        'templates.json']
    
    def test_correct_by_id(self):
        """Filter by ID."""
        #http://vct:8888/api/slivers/?/slice/id=1
        url = reverse('sliver-list')
        resp = self.client.get(url + '?/slice/id=1')
        self.assertEqual(resp.status_code, 200)
        sliver_js = json.loads(resp.content)
        
        # check number objects returned
        sliver_qs = Sliver.objects.filter(slice_id=1)
        self.assertEqual(len(sliver_js), sliver_qs.count())
        
        # check if objects return really match
        for slv in sliver_js:
            self.assertEqual(slv['slice']['id'], 1)
    
    def test_correct_against_array(self):
        """Filter by nested list's attribute."""
        #http://vct:8888/api/slivers/?/interfaces/_/type="public4"
        url = reverse('sliver-list')
        resp = self.client.get(url + '?/interfaces/_/type="public4"')
        self.assertEqual(resp.status_code, 200)
        sliver_js = json.loads(resp.content)
        
        # check number objects returned
        sliver_qs = Sliver.objects.filter(interfaces__type="public4")
        self.assertEqual(len(sliver_js), sliver_qs.count())
        
        # check if objects return really match
        for slv in sliver_js:
            matchs = False
            for ifaces in slv['interfaces']:
                if ifaces['type'] == 'public4':
                    matchs = True
                    break
            self.assertTrue(matchs)

    def test_correct_multiple_conditions(self):
        """Several matches may be specified, they are ANDed together."""
        #http://vct:8888/api/slivers/?/node/id=2&/interfaces/_/type="public4"
        url = reverse('sliver-list')
        resp = self.client.get(url + '?node/id=2&/interfaces/_/type="public4"')
        self.assertEqual(resp.status_code, 200)
        sliver_js = json.loads(resp.content)
        
        # check number objects returned
        sliver_qs = Sliver.objects.filter(node_id=2, interfaces__type="public4")
        self.assertEqual(len(sliver_js), sliver_qs.count())
        
        # check if objects return really match
        for slv in sliver_js:
            self.assertEqual(slv['node']['id'], 2)
            matchs = False
            for ifaces in slv['interfaces']:
                if ifaces['type'] == 'public4':
                    matchs = True
                    break
            self.assertTrue(matchs)
    
    def test_correct_string_value(self):
        """String query."""
        #http://vct:8888/api/nodes/?/name="the yeah node"
        url = reverse('node-list')
        resp = self.client.get(url + '?/name="Basibe"')
        self.assertEqual(resp.status_code, 200)
        node_js = json.loads(resp.content)
        
        # check number objects returned
        node_qs = Node.objects.filter(name="Basibe")
        self.assertEqual(len(node_js), node_qs.count())
        
        # check if objects return really match
        for node in node_js:
            self.assertEqual(node['name'], "Basibe")
    
    def test_correct_multiple_objects(self):
        """String query."""
        #http://vct:8888/api/nodes/?/set_state="production"
        url = reverse('node-list')
        resp = self.client.get(url + '?/set_state="production"')
        self.assertEqual(resp.status_code, 200)
        node_js = json.loads(resp.content)
        
        # check number objects returned
        node_qs = Node.objects.filter(set_state="production")
        self.assertEqual(len(node_js), node_qs.count())
        
        # check if objects return really match
        for node in node_js:
            self.assertEqual(node['set_state'], "production")
    
    def test_correct_string_double_quotes(self):
        """String with double quotes."""
        #http://vct:8888/api/nodes/?/name="double ""quotes"""
        url = reverse('node-list')
        resp = self.client.get(url + '?/name="double ""quotes""')
        self.assertEqual(resp.status_code, 200)
        node_js = json.loads(resp.content)
        
        # check number objects returned
        node_qs = Node.objects.filter(name='double "quotes"')
        self.assertEqual(len(node_js), node_qs.count())
        
        # check if objects return really match
        for node in node_js:
            self.assertEqual(node['name'], 'double "quotes"')

    def test_incorrect_non_existing_field(self):
        """Non existing field."""
        #http://vct:8888/api/nodes/?/not_existing_field="foo"
        url = reverse('node-list')
        resp = self.client.get(url + '?/not_existing_field="foo"')
        self.assertEqual(resp.status_code, 422)
    
    def test_incorrect_unmatching_type(self):
        """Invalid types."""
        #http://vct:8888/api/nodes/?/id="foo"  # ID should be an integer
        url = reverse('node-list')
        resp = self.client.get(url + '?/id="foo"')
        self.assertEqual(resp.status_code, 422)
        
        #http://vct:8888/api/nodes/?/name=foo  # string without dobule quotes
        url = reverse('node-list')
        resp = self.client.get(url + '?/name=foo')
        self.assertEqual(resp.status_code, 422)
