# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Resource'
        db.create_table(u'resources_resource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('max_req', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('dflt_req', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'resources', ['Resource'])

        # Adding unique constraint on 'Resource', fields ['name', 'object_id', 'content_type']
        db.create_unique(u'resources_resource', ['name', 'object_id', 'content_type_id'])

        # Adding model 'ResourceReq'
        db.create_table(u'resources_resourcereq', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('req', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'resources', ['ResourceReq'])


    def backwards(self, orm):
        # Removing unique constraint on 'Resource', fields ['name', 'object_id', 'content_type']
        db.delete_unique(u'resources_resource', ['name', 'object_id', 'content_type_id'])

        # Deleting model 'Resource'
        db.delete_table(u'resources_resource')

        # Deleting model 'ResourceReq'
        db.delete_table(u'resources_resourcereq')


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
            'dflt_req': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_req': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
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