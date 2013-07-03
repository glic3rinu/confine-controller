# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Notification.message'
        db.delete_column(u'notifications_notification', 'message')

        # Adding field 'Notification.subject'
        db.add_column(u'notifications_notification', 'subject',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256),
                      keep_default=False)

        # Adding field 'Notification.content'
        db.add_column(u'notifications_notification', 'content',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Notification.message'
        raise RuntimeError("Cannot reverse this migration. 'Notification.message' and its values cannot be restored.")
        # Deleting field 'Notification.subject'
        db.delete_column(u'notifications_notification', 'subject')

        # Deleting field 'Notification.content'
        db.delete_column(u'notifications_notification', 'content')


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
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'blank': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['notifications']