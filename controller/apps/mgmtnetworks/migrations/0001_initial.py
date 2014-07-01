# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("tinc", "0013_auto__del_island"),
    )

    def forwards(self, orm):
        # Adding model 'MgmtNetConf'
        db.create_table(u'mgmtnetworks_mgmtnetconf', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('backend', self.gf('django.db.models.fields.CharField')(default='tinc', max_length=16)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'mgmtnetworks', ['MgmtNetConf'])

        # Adding unique constraint on 'MgmtNetConf', fields ['content_type', 'object_id']
        db.create_unique(u'mgmtnetworks_mgmtnetconf', ['content_type_id', 'object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'MgmtNetConf', fields ['content_type', 'object_id']
        db.delete_unique(u'mgmtnetworks_mgmtnetconf', ['content_type_id', 'object_id'])

        # Deleting model 'MgmtNetConf'
        db.delete_table(u'mgmtnetworks_mgmtnetconf')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'mgmtnetworks.mgmtnetconf': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'MgmtNetConf'},
            'backend': ('django.db.models.fields.CharField', [], {'default': "'tinc'", 'max_length': '16'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['mgmtnetworks']
