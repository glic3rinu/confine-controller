# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'NodeState'
        db.delete_table(u'state_nodestate')

        # Deleting model 'SliverState'
        db.delete_table(u'state_sliverstate')

        # Adding model 'StateHistory'
        db.create_table(u'state_statehistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['state.State'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'state', ['StateHistory'])

        # Adding model 'State'
        db.create_table(u'state_state', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('last_seen_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_try_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_contact_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('metadata', self.gf('django.db.models.fields.TextField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'state', ['State'])

        # Adding unique constraint on 'State', fields ['content_type', 'object_id']
        db.create_unique(u'state_state', ['content_type_id', 'object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'State', fields ['content_type', 'object_id']
        db.delete_unique(u'state_state', ['content_type_id', 'object_id'])

        # Adding model 'NodeState'
        db.create_table(u'state_nodestate', (
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(related_name='state', unique=True, primary_key=True, to=orm['nodes.Node'])),
            ('last_change_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_contact_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('soft_version', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_try_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_seen_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('metadata', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'state', ['NodeState'])

        # Adding model 'SliverState'
        db.create_table(u'state_sliverstate', (
            ('last_change_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('add_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_try_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_seen_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('sliver', self.gf('django.db.models.fields.related.OneToOneField')(related_name='state', unique=True, primary_key=True, to=orm['slices.Sliver'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('metadata', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'state', ['SliverState'])

        # Deleting model 'StateHistory'
        db.delete_table(u'state_statehistory')

        # Deleting model 'State'
        db.delete_table(u'state_state')


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
            'Meta': {'ordering': "['-date']", 'object_name': 'StateHistory'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['state.State']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['state']