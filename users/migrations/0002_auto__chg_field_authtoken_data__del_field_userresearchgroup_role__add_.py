# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'AuthToken.data'
        db.alter_column(u'users_authtoken', 'data', self.gf('django.db.models.fields.TextField')())
        # Deleting field 'UserResearchGroup.role'
        db.delete_column(u'users_userresearchgroup', 'role_id')

        # Adding M2M table for field roles on 'UserResearchGroup'
        db.create_table(u'users_userresearchgroup_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userresearchgroup', models.ForeignKey(orm[u'users.userresearchgroup'], null=False)),
            ('role', models.ForeignKey(orm[u'users.role'], null=False))
        ))
        db.create_unique(u'users_userresearchgroup_roles', ['userresearchgroup_id', 'role_id'])

        # Adding unique constraint on 'UserResearchGroup', fields ['user', 'research_group']
        db.create_unique(u'users_userresearchgroup', ['user_id', 'research_group_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserResearchGroup', fields ['user', 'research_group']
        db.delete_unique(u'users_userresearchgroup', ['user_id', 'research_group_id'])


        # Changing field 'AuthToken.data'
        db.alter_column(u'users_authtoken', 'data', self.gf('django.db.models.fields.CharField')(max_length=256))
        # Adding field 'UserResearchGroup.role'
        db.add_column(u'users_userresearchgroup', 'role',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['users.Role']),
                      keep_default=False)

        # Removing M2M table for field roles on 'UserResearchGroup'
        db.delete_table('users_userresearchgroup_roles')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'users.authtoken': {
            'Meta': {'object_name': 'AuthToken'},
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
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

    complete_apps = ['users']