"""
Tests for pings app using the unittest module.
These will pass when you run "manage.py test".
"""
import random
import string
import time

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from controller.core.exceptions import OperationLocked
from users.models import Group
from nodes.models import Node

from .models import Ping
from .tasks import ping as ping_task

class PingTests(TestCase):
    def random_number(self, length=4):
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_on_cascade_deletion(self):
        # Pings objects not deleted on cascade #448
        # http://redmine.confine-project.eu/issues/448
        
        # Create a node
        group = Group.objects.create(name='group_%s' % self.random_number())
        node = Node.objects.create(name='node_%s' % self.random_number, group=group)
        
        # get related values
        mgmt_net = node.mgmt_net
        ctype = ContentType.objects.get_for_model(mgmt_net)
        typed_pings = Ping.objects.filter(content_type=ctype)

        # Wait until pings are created
        timeout = 0
        while not typed_pings.filter(object_id=mgmt_net.pk).exists():
            try:
                # run task manually to force pings generation
                ping_task('mgmtnetworks.mgmtnetconf', ids=[mgmt_net.pk])
            except OperationLocked:
                pass # task is alreday being executed
            time.sleep(1)
            self.assertTrue(timeout < 60)
            timeout +=1

        # remove the node
        node.delete()

        # related objects should NOT exist
        self.assertFalse(typed_pings.filter(object_id=mgmt_net.pk).exists(),
            "Pings has NOT been removed!")