import gevent
import requests

from django.test import LiveServerTestCase

from nodes.models import Node
from users.models import Group

from .helpers import extract_node_software_version, sizeof_fmt
from .models import State
from .settings import STATE_NODE_SOFT_VERSION_URL, STATE_NODE_SOFT_VERSION_NAME

class StateTest(LiveServerTestCase):
    def setUp(self):
        group = Group.objects.create(name='Group', allow_nodes=True)
        self.node = Node.objects.create(name='Test', group=group)
    
    def test_store_glet(self):
        """Tests State.store_glet (#468)"""
        glet = gevent.spawn(requests.get, self.live_server_url, headers={})
        gevent.joinall([glet])
        # Should work without raising TypeError exception (#468)
        # CaseInsensitiveDict is not JSON serializable
        try:
            State.store_glet(self.node, glet)
        except TypeError as e:
            self.fail('State.store_glet() raised TypeError: %s' % e)
    
    def test_helper_sizeof_fmt(self):
        # Test helper used by disk_available (#339)
        self.assertIn('MB', sizeof_fmt(0))
        self.assertIn('GB', sizeof_fmt(-1 * 2**10))
        self.assertIn('GB', sizeof_fmt(2**10))
        self.assertIn('TB', sizeof_fmt(2**20))
        self.assertIn('TB', sizeof_fmt(2**50))
        self.assertEquals('N/A', sizeof_fmt('N/A'))
    
    def test_node_soft_version(self):
        # master-trunk.f1a07e0-r20140213.0946-1
        NODE_SCHEMA = "%(branch)s.%(rev)s-%(date)s-%(pkg)s"
        NODE_VERSIONS = [
            # branch with a dot '.'
            {'branch': 'master.trunk' , 'rev': 'f1a07e0', 'date': 'r20140213.0946', 'pkg': '1'},
            # branch with a dash '-'
            {'branch': 'master-trunk' , 'rev': '1130af0', 'date': 'r20130911.0946', 'pkg': '1'},
            # empty branch name
            {'branch': '' , 'rev': '1234567', 'date': 'r20131101.0826', 'pkg': '1'},
            # empty data
            {'branch': '' , 'rev': '', 'date': '', 'pkg': ''},
        ]
        for node_version in NODE_VERSIONS:
            version_raw = NODE_SCHEMA % node_version
            version = extract_node_software_version(version_raw)
            self.assertEquals(version, node_version)
            
            # Try to generate url and name based on settings
            STATE_NODE_SOFT_VERSION_URL(version)
            STATE_NODE_SOFT_VERSION_NAME(version)
