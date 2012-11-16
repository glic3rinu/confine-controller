# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Message.author'
        db.alter_column(u'issues_message', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User']))

        # Changing field 'Ticket.created_by'
        db.alter_column(u'issues_ticket', 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User']))

        # Changing field 'Ticket.owner'
        db.alter_column(u'issues_ticket', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['users.User']))

    def backwards(self, orm):

        # Changing field 'Message.author'
        db.alter_column(u'issues_message', 'author_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Ticket.created_by'
        db.alter_column(u'issues_ticket', 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Ticket.owner'
        db.alter_column(u'issues_ticket', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'issues.message': {
            'Meta': {'object_name': 'Message'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['issues.Ticket']"}),
            'visibility': ('django.db.models.fields.CharField', [], {'default': "'PUBLIC'", 'max_length': '32'})
        },
        u'issues.queue': {
            'Meta': {'object_name': 'Queue'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'issues.ticket': {
            'Meta': {'ordering': "['-last_modified_on']", 'object_name': 'Ticket'},
            'cc': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_tickets_set'", 'null': 'True', 'to': u"orm['users.User']"}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'MEDIUM'", 'max_length': '32'}),
            'queue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['issues.Queue']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '32'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'users.permission': {
            'Meta': {'object_name': 'Permission'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'testbedpermission_set'", 'to': u"orm['contenttypes.ContentType']"}),
            'evaluation': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'users.researchgroup': {
            'Meta': {'object_name': 'ResearchGroup'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'postal_code': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'users.role': {
            'Meta': {'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.Permission']", 'symmetrical': 'False'})
        },
        u'users.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'research_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.ResearchGroup']", 'symmetrical': 'False', 'through': u"orm['users.UserResearchGroup']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36', 'blank': 'True'})
        },
        u'users.userresearchgroup': {
            'Meta': {'unique_together': "(('user', 'research_group'),)", 'object_name': 'UserResearchGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'research_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.ResearchGroup']"}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.Role']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
        }
    }

    complete_apps = ['issues']