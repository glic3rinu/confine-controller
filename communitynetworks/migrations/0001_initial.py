# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CnHost'
        db.create_table(u'communitynetworks_cnhost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('cndb_uri', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('cndb_cached_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=36)),
        ))
        db.send_create_signal(u'communitynetworks', ['CnHost'])

        # Adding unique constraint on 'CnHost', fields ['content_type', 'object_id']
        db.create_unique(u'communitynetworks_cnhost', ['content_type_id', 'object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CnHost', fields ['content_type', 'object_id']
        db.delete_unique(u'communitynetworks_cnhost', ['content_type_id', 'object_id'])

        # Deleting model 'CnHost'
        db.delete_table(u'communitynetworks_cnhost')


    models = {
        u'communitynetworks.cnhost': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'CnHost'},
            'app_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '36'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['communitynetworks']