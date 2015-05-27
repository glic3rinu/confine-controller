# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Ping', fields ['object_id', 'content_type']
        db.create_index(u'pings_ping', ['object_id', 'content_type_id'])


    def backwards(self, orm):
        # Removing index on 'Ping', fields ['object_id', 'content_type']
        db.delete_index(u'pings_ping', ['object_id', 'content_type_id'])


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pings.ping': {
            'Meta': {'object_name': 'Ping', 'index_together': "[['object_id', 'content_type'], ['object_id', 'content_type', 'date']]"},
            'avg': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'mdev': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'min': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'packet_loss': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'samples': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4'})
        }
    }

    complete_apps = ['pings']