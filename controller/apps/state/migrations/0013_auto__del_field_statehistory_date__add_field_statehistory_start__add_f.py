# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.utils import timezone


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'StateHistory.date'
        db.delete_column(u'state_statehistory', 'date')

        # Adding field 'StateHistory.start'
        db.add_column(u'state_statehistory', 'start',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True,
                        default=datetime.datetime(2013, 9, 15, 0, 0, tzinfo=timezone.get_default_timezone()), blank=True),
                      keep_default=False)

        # Adding field 'StateHistory.end'
        db.add_column(u'state_statehistory', 'end',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True,
                        default=datetime.datetime(2013, 9, 15, 0, 0, tzinfo=timezone.get_default_timezone()), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'StateHistory.date'
        db.add_column(u'state_statehistory', 'date',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2013, 9, 15, 0, 0), blank=True),
                      keep_default=False)

        # Deleting field 'StateHistory.start'
        db.delete_column(u'state_statehistory', 'start')

        # Deleting field 'StateHistory.end'
        db.delete_column(u'state_statehistory', 'end')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'notifications.delivered': {
            'Meta': {'object_name': 'Delivered'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delivered'", 'to': u"orm['notifications.Notification']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'notifications.notification': {
            'Meta': {'object_name': 'Notification'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'state.state': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'State'},
            'add_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_contact_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_seen_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'last_try_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'state.statehistory': {
            'Meta': {'ordering': "['-start']", 'object_name': 'StateHistory'},
            'end': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': u"orm['state.State']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['state']
