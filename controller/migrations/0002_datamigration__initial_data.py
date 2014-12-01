# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from controller.settings import MGMT_IPV6_PREFIX

class Migration(DataMigration):

    def forwards(self, orm):
        "Initialize testbed singlenton and its parameters."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        testbed, _ = orm.Testbed.objects.get_or_create()
        orm.TestbedParams.objects.get_or_create(testbed=testbed)

    def backwards(self, orm):
        "Drop testbed singlenton."
        testbed = orm.Testbed.objects.get()
        orm.TestbedParams.objects.filter(testbed=testbed).delete()
        testbed.delete()

    models = {
        u'controller.testbed': {
            'Meta': {'object_name': 'Testbed'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'controller.testbedparams': {
            'Meta': {'object_name': 'TestbedParams'},
            'mgmt_ipv6_prefix': ('django.db.models.fields.CharField', [], {'default': "'fd65:fc41:c50f::/48'", 'max_length': '128'}),
            'testbed': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'testbed_params'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['controller.Testbed']"})
        }
    }

    complete_apps = ['controller']
    symmetrical = True
