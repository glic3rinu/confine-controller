import gevent
import requests

from django.test import LiveServerTestCase

from nodes.models import Node
from users.models import Group

from .models import State

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
