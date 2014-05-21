# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Message.author_name'
        db.add_column(u'issues_message', 'author_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=60),
                      keep_default=False)


        # Changing field 'Message.author'
        db.alter_column(u'issues_message', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'], null=True, on_delete=models.SET_NULL))
        # Adding field 'Ticket.created_by_name'
        db.add_column(u'issues_ticket', 'created_by_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=60),
                      keep_default=False)


        # Changing field 'Ticket.created_by'
        db.alter_column(u'issues_ticket', 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['users.User']))

    def backwards(self, orm):
        # Deleting field 'Message.author_name'
        db.delete_column(u'issues_message', 'author_name')


        # User chose to not deal with backwards NULL issues for 'Message.author'
        if orm.Message.objects.filter(author__isnull=True).exists():
            raise RuntimeError("Cannot reverse this migration. 'Message.author' and its values cannot be restored."
                "If you want to undo, handle Messages with null author (i.e. 'Message.author__isnull=True)")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Message.author'
        db.alter_column(u'issues_message', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User']))
        # Deleting field 'Ticket.created_by_name'
        db.delete_column(u'issues_ticket', 'created_by_name')


        # User chose to not deal with backwards NULL issues for 'Ticket.created_by'
        if orm.Ticket.objects.filter(created_by__isnull=True).exists():
            raise RuntimeError("Cannot reverse this migration. 'Ticket.created_by' and its values cannot be restored."
                "If you want to undo, handle Tickets with null created_by (i.e. 'Ticket.created_by__isnull=True)")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Ticket.created_by'
        db.alter_column(u'issues_ticket', 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User']))

    models = {
        u'issues.message': {
            'Meta': {'object_name': 'Message'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['issues.Ticket']"})
        },
        u'issues.queue': {
            'Meta': {'object_name': 'Queue'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'notify_group_admins': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_node_admins': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_slice_admins': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'issues.ticket': {
            'Meta': {'ordering': "['-last_modified_on']", 'object_name': 'Ticket'},
            'cc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_tickets'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['users.User']"}),
            'created_by_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assigned_tickets'", 'null': 'True', 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_tickets'", 'null': 'True', 'to': u"orm['users.User']"}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'MEDIUM'", 'max_length': '32'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tickets'", 'null': 'True', 'to': u"orm['issues.Queue']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '32'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'visibility': ('django.db.models.fields.CharField', [], {'default': "'PUBLIC'", 'max_length': '32'})
        },
        u'issues.tickettracker': {
            'Meta': {'unique_together': "(('ticket', 'user'),)", 'object_name': 'TicketTracker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['issues.Ticket']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
        },
        u'users.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'users.roles': {
            'Meta': {'unique_together': "(('user', 'group'),)", 'object_name': 'Roles'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_group_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_node_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_slice_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['users.User']"})
        },
        u'users.user': {
            'Meta': {'ordering': "['name']", 'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'through': u"orm['users.Roles']", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('controller.models.fields.TrimmedCharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('controller.models.fields.NullableCharField', [], {'db_index': 'True', 'max_length': '30', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['issues']
