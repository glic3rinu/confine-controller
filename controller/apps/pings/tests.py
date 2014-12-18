"""
Tests for pings app using the unittest module.
These will pass when you run "manage.py test".
"""
import json
import random
import string
import time

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import skipUnlessDBFeature, TestCase
from django.utils import timezone

from controller.core.exceptions import OperationLocked
from users.models import Group, User
from nodes.models import Node

from .models import Ping
from .tasks import ping as ping_task

class PingTests(TestCase):
    fixtures = ['groups.json', 'users.json', 'roles.json']
    
    def random_number(self, length=4):
        return ''.join(random.choice(string.digits) for _ in range(length))
    
    def setUp(self):
        """
        By default the tests are executed as unprivileged user
        """
        # Update the passwords to be usable during testing
        # because fixture and test can have different PASSWORD_HASHERS
        for user in User.objects.all():
            user.set_password("%spass" % user.username)
            user.save()
        logged = self.client.login(username='user', password='userpass')
        self.assertTrue(logged, "Logging in user failed.")
    
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
    
    # sqlite doesn't support extract epoch but django
    # doesn't implements 'date_extract_sql' yet so we
    # chose a feature supported by postgresql but
    # not by sqlite to do the trick.
    @skipUnlessDBFeature('supports_timezones')
    def test_timeseries_json_serializer(self):
        """Check that JSON serializes Decimal as a numeric value."""
        # Create ping object
        group = Group.objects.create(name='group_%s' % self.random_number())
        node = Node.objects.create(name='node_%s' % self.random_number(), group=group)
        
        ctype_id = ContentType.objects.get_for_model(node.mgmt_net).pk
        object_id = node.mgmt_net.pk
        
        ping = Ping.objects.create(content_type_id=ctype_id, object_id=object_id,
            packet_loss=0, min=0.123, max=9.123, avg=4.567, mdev=0.2, date=timezone.now())
        
        # get timeseries view
        kwargs = dict(content_type_id=ctype_id, object_id=object_id)
        url = reverse('admin:pings_ping_timeseries', kwargs=kwargs)
        resp = self.client.get(url)
        resp_js = json.loads(resp.content)
        
        # highcharts JS expects data to be numeric
        for epoch, loss, rtt_avg, rtt_min, rtt_max in resp_js:
            self.assertIsInstance(rtt_avg, float)
            self.assertIsInstance(rtt_min, float)
            self.assertIsInstance(rtt_max, float)
