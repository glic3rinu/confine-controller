# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Resource', fields ['name']
        db.delete_unique(u'resources_resource', ['name'])

        # Adding unique constraint on 'ResourceReq', fields ['content_type', 'name', 'object_id']
        db.create_unique(u'resources_resourcereq', ['content_type_id', 'name', 'object_id'])

        # Adding unique constraint on 'Resource', fields ['content_type', 'name', 'object_id']
        db.create_unique(u'resources_resource', ['content_type_id', 'name', 'object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Resource', fields ['content_type', 'name', 'object_id']
        db.delete_unique(u'resources_resource', ['content_type_id', 'name', 'object_id'])

        # Removing unique constraint on 'ResourceReq', fields ['content_type', 'name', 'object_id']
        db.delete_unique(u'resources_resourcereq', ['content_type_id', 'name', 'object_id'])

        # Adding unique constraint on 'Resource', fields ['name']
        db.create_unique(u'resources_resource', ['name'])


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
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'resources.resourcereq': {
            'Meta': {'unique_together': "(['name', 'object_id', 'content_type'],)", 'object_name': 'ResourceReq'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'req': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['resources']