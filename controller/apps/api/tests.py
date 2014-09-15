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


import urlparse, sys
class PaginationTests(TestCase):
    fixtures = ['groups.json', 'nodes.json', 'slices.json', 'slivers.json',
        'templates.json']
    
    def get_page(self, url):
        url = urlparse.urlparse(url)
        query = dict(urlparse.parse_qsl(url.query))
        return int(query['page'])
        
    
    def check_pagination_links(self, header_link, current_page=1):
        value, rel = zip(*[link.split('; ') for link in header_link.split(', ')])
        value = [val.lstrip("<").rstrip(">") for val in value]
        rel = [r.split('=')[1].strip('"') for r in rel]
        
        # headers should always include first, last links
        self.assertIn('first', rel)
        self.assertIn('last', rel)
        
        # headers may include next, prev links
        first_page = self.get_page(value[rel.index('first')])
        last_page = self.get_page(value[rel.index('last')])
        if current_page > first_page:
            self.assertIn('prev', rel)
        if current_page < last_page:
            self.assertIn('next', rel)
    
    def test_correct_default_pagination(self):
        url = reverse('node-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])

    def test_correct_invalid_page(self):
        url = reverse('node-list')
        resp = self.client.get(url + '?page=-1')
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])
        
        # FIXME: replace sys.maxsize by last_page + 1
        resp = self.client.get(url + '?page=%i' % sys.maxsize)
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])
    
    def test_correct_invalid_per_page(self):
        url = reverse('node-list')
        resp = self.client.get(url + '?per_page=0')
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])
        
        url = reverse('node-list')
        resp = self.client.get(url + '?per_page=NaN')
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])
