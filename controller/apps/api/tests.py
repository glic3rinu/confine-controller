"""
Test controller api app.
"""
import json
import urlparse

from django.core.urlresolvers import reverse
from django.test import TestCase

from nodes.models import Node
from slices.models import Sliver

from .utils.profiles import _Profile, profile_matches


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


class PaginationTests(TestCase):
    fixtures = ['groups.json', 'nodes.json']
    
    def get_page(self, url):
        url = urlparse.urlparse(url)
        query = dict(urlparse.parse_qsl(url.query))
        return int(query['page'])
    
    def extract_header_links(self, header_link):
        """Process response and return dictionary links"""
        value, rel = zip(*[link.split('; ') for link in header_link.split(', ')])
        value = [val.lstrip("<").rstrip(">") for val in value]
        rel = [r.split('=')[1].strip('"') for r in rel]
        return dict(zip(rel, value))
    
    def check_pagination_links(self, header_link, current_page=1):
        """
        Check that header includes links to other pages of
        the listing.
        
        """
        links = self.extract_header_links(header_link)
        
        # headers should always include first, last links
        self.assertIn('first', links)
        self.assertIn('last', links)
        
        # headers may include next, prev links
        first_page = self.get_page(links['first'])
        last_page = self.get_page(links['last'])
        if current_page > first_page:
            self.assertIn('prev', links)
        if current_page < last_page:
            self.assertIn('next', links)
        
        return links
    
    def test_correct_default_pagination(self):
        """Test pagination with implicit page and per_page."""
        url = reverse('node-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])

    def test_correct_invalid_page(self):
        """Test pagination with page < 1 and page > MAX."""
        url = reverse('node-list')
        resp = self.client.get(url + '?page=-1')
        self.assertEqual(resp.status_code, 200)
        links = self.check_pagination_links(resp['Link'])
        
        last_page = self.get_page(links['last'])
        resp = self.client.get('%s?page=%i' % (url, last_page + 1))
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])
    
    def test_correct_invalid_per_page(self):
        """Test pagination with invalid per_page values."""
        url = reverse('node-list')
        resp = self.client.get(url + '?per_page=0')
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])
        
        resp = self.client.get(url + '?per_page=NaN')
        self.assertEqual(resp.status_code, 200)
        self.check_pagination_links(resp['Link'])
    
    def test_follow_pagination_links(self):
        """Test follow next and prev link collecting all objects."""
        url = reverse('node-list')
        resp = self.client.get(url + '?per_page=3')
        links = self.check_pagination_links(resp['Link'])
        
        # follow forwards
        nodes = []
        current_page = 1
        last_page = self.get_page(links['last'])
        while True:
            resp = self.client.get(url + '?per_page=3&page=%i' % current_page)
            nodes += json.loads(resp.content)
            links = self.check_pagination_links(resp['Link'], current_page)
            if current_page == last_page:
                break
            current_page = self.get_page(links['next'])
        
        nodes_db = set(Node.objects.values_list('id', flat=True))
        nodes_id = set([node['id'] for node in nodes])
        self.assertEquals(nodes_db, nodes_id)
        
        # follow backwards
        nodes = []
        current_page = self.get_page(links['last'])
        first_page = self.get_page(links['first'])
        while True:
            resp = self.client.get(url + '?per_page=3&page=%i' % current_page)
            nodes += json.loads(resp.content)
            links = self.check_pagination_links(resp['Link'], current_page)
            if current_page == first_page:
                break
            current_page = self.get_page(links['prev'])
        
        nodes_db = set(Node.objects.values_list('id', flat=True))
        nodes_id = set([node['id'] for node in nodes])
        self.assertEquals(nodes_db, nodes_id)
    
    def test_paginate_empty_queryset(self):
        # Regression test ZeroDivisionError
        assert not Sliver.objects.exists(), "Slivers queryset is not empty."
        url = reverse('sliver-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class IntegrationTests(TestCase):
    fixtures = ['groups.json', 'nodes.json']
    
    def test_pagination_with_filtering(self):
        """
        Test combination of pagination and filtering.
        Expected result: 2 pages with 1 node per page.
        
        """
        url = reverse('node-list')
        filter_query = '/set_state="production"'
        pagination = 'per_page=1&page=2'
        url_query = '&'.join([filter_query, pagination])
        
        resp = self.client.get("%s?%s" % (url, url_query))
        self.assertEqual(resp.status_code, 200)
        node_js = json.loads(resp.content)
        
        # check number objects returned
        node_qs = Node.objects.filter(set_state="production")[1:2]
        self.assertEqual(len(node_js), node_qs.count())
        
        # check if objects return really match
        for node in node_js:
            self.assertEqual(node['set_state'], "production")
    
    def test_pagination_filtering_member_selection(self):
        url = reverse('node-list')
        filter_query = '/set_state="production"'
        pagination = 'per_page=1&page=2'
        member_query = 'show=/name,/set_state'
        url_query = '&'.join([filter_query, pagination, member_query])
        
        resp = self.client.get("%s?%s" % (url, url_query))
        self.assertEqual(resp.status_code, 200)
        node_js = json.loads(resp.content)
        
        # check number objects returned
        node_qs = Node.objects.filter(set_state="production")[1:2]
        self.assertEqual(len(node_js), node_qs.count())
        
        # check if objects return really match
        for node in node_js:
            self.assertEqual(node['set_state'], "production")
        
        #TODO extend test when member selection implemented


class MemberSelectionTests(TestCase):
    fixtures = ['groups.json']
    
    def test_basic_member_selection(self):
        url = reverse('group-list')
        member_query = 'show=/name'
        resp = self.client.get(url + '?%s' % member_query)
        self.assertEqual(resp.status_code, 200)
        #TODO extend test when member selection implemented


class ProfileTests(TestCase):
    
    def assertEqual_schema_profile(self, schema):
        profile = _Profile(schema['uri'])
        self.assertEqual(schema['api'], profile.api)
        self.assertEqual(schema['version'], profile.version)
        self.assertEqual(schema['resource'], profile.resource)
    
    def test_parse_full_profile_uri(self):
        schema = {
            'uri': "http://confine-project.eu/schema/registry/v0/base",
            'api': 'registry',
            'version': 'v0',
            'resource': 'base',
        }
        self.assertEqual_schema_profile(schema)
    
    def test_parse_profile_version_less_uri(self):
        schema = {
            'uri': "http://confine-project.eu/schema/registry/base",
            'api': 'registry',
            'version': None,
            'resource': 'base',
        }
        self.assertEqual_schema_profile(schema)
    
    def test_parse_resource_list_profile_uri(self):
        schema = {
            'uri': "http://confine-project.eu/schema/registry/v3/resource-list",
            'api': 'registry',
            'version': 'v3',
            'resource': 'resource-list',
        }
        self.assertEqual_schema_profile(schema)
    
    def test_parse_invalid_profile_uri(self):
        self.assertRaises(ValueError, _Profile, "http://foo.go")
    
    def test_matching_profiles_version_less(self):
        first = "http://confine-project.eu/schema/registry/v3/node"
        other = "http://confine-project.eu/schema/registry/node"
        self.assertTrue(profile_matches(first, other))
    
    def test_matching_profiles_none(self):
        first = None
        other = "http://confine-project.eu/schema/registry/node"
        self.assertTrue(profile_matches(first, other))
    
    def test_not_matching_profiles(self):
        first = "http://confine-project.eu/schema/registry/v3/node"
        other = "http://confine-project.eu/schema/registry/v0/node"
        self.assertFalse(profile_matches(first, other))
