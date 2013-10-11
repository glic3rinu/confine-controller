# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TimeSerie'
        db.create_table(u'monitor_timeserie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('value', self.gf('jsonfield.fields.JSONField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'monitor', ['TimeSerie'])

        # Adding index on 'TimeSerie', fields ['name', 'date']
        db.create_index(u'monitor_timeserie', ['name', 'date'])


    def backwards(self, orm):
        # Removing index on 'TimeSerie', fields ['name', 'date']
        db.delete_index(u'monitor_timeserie', ['name', 'date'])

        # Deleting model 'TimeSerie'
        db.delete_table(u'monitor_timeserie')


    models = {
        u'monitor.timeserie': {
            'Meta': {'object_name': 'TimeSerie', 'index_together': "[['name', 'date']]"},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'value': ('jsonfield.fields.JSONField', [], {})
        }
    }

    complete_apps = ['monitor']