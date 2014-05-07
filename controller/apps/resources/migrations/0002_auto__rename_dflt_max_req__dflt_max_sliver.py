# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Renaming 'Resource.dflt_req' to 'dflt_sliver'
        db.rename_column(u'resources_resource', 'dflt_req', 'dflt_sliver')

        # Renaming 'Resource.max_req' to 'max_sliver'
        db.rename_column(u'resources_resource', 'max_req', 'max_sliver')


    def backwards(self, orm):
        # Renaming 'Resource.dflt_req' to 'dflt_sliver'
        db.rename_column(u'resources_resource', 'dflt_sliver', 'dflt_req')

        # Renaming 'Resource.max_req' to 'max_sliver'
        db.rename_column(u'resources_resource', 'max_sliver', 'max_req')



    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'resources.resource': {
            'Meta': {'unique_together': "(['name', 'object_id', 'content_type'],)", 'object_name': 'Resource'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'dflt_sliver': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_sliver': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'resources.resourcereq': {
            'Meta': {'object_name': 'ResourceReq'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'req': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['resources']
