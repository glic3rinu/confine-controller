# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("resources", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'Testbed'
        db.create_table(u'controller_testbed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'controller', ['Testbed'])

        # Adding model 'TestbedParams'
        db.create_table(u'controller_testbedparams', (
            ('testbed', self.gf('django.db.models.fields.related.OneToOneField')(related_name='testbed_params', unique=True, primary_key=True, to=orm['controller.Testbed'])),
            ('mgmt_ipv6_prefix', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'controller', ['TestbedParams'])


    def backwards(self, orm):
        # Deleting model 'Testbed'
        db.delete_table(u'controller_testbed')

        # Deleting model 'TestbedParams'
        db.delete_table(u'controller_testbedparams')


    models = {
        u'controller.testbed': {
            'Meta': {'object_name': 'Testbed'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'controller.testbedparams': {
            'Meta': {'object_name': 'TestbedParams'},
            'mgmt_ipv6_prefix': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'testbed': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'testbed_params'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['controller.Testbed']"})
        }
    }

    complete_apps = ['controller']
