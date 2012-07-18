# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ActivationRequest'
        db.create_table('user_management_activationrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('user_management', ['ActivationRequest'])

        # Adding model 'DeleteRequest'
        db.create_table('user_management_deleterequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('user_management', ['DeleteRequest'])

        # Adding model 'ResearchGroup'
        db.create_table('user_management_researchgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
        ))
        db.send_create_signal('user_management', ['ResearchGroup'])

        # Adding M2M table for field users on 'ResearchGroup'
        db.create_table('user_management_researchgroup_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('researchgroup', models.ForeignKey(orm['user_management.researchgroup'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('user_management_researchgroup_users', ['researchgroup_id', 'user_id'])

        # Adding model 'Role'
        db.create_table('user_management_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('research_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_management.ResearchGroup'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('user_management', ['Role'])

        # Adding M2M table for field users on 'Role'
        db.create_table('user_management_role_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm['user_management.role'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('user_management_role_users', ['role_id', 'user_id'])

        # Adding model 'ConfinePermission'
        db.create_table('user_management_confinepermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('permission', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('user_management', ['ConfinePermission'])

        # Adding M2M table for field role on 'ConfinePermission'
        db.create_table('user_management_confinepermission_role', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('confinepermission', models.ForeignKey(orm['user_management.confinepermission'], null=False)),
            ('role', models.ForeignKey(orm['user_management.role'], null=False))
        ))
        db.create_unique('user_management_confinepermission_role', ['confinepermission_id', 'role_id'])

    def backwards(self, orm):
        # Deleting model 'ActivationRequest'
        db.delete_table('user_management_activationrequest')

        # Deleting model 'DeleteRequest'
        db.delete_table('user_management_deleterequest')

        # Deleting model 'ResearchGroup'
        db.delete_table('user_management_researchgroup')

        # Removing M2M table for field users on 'ResearchGroup'
        db.delete_table('user_management_researchgroup_users')

        # Deleting model 'Role'
        db.delete_table('user_management_role')

        # Removing M2M table for field users on 'Role'
        db.delete_table('user_management_role_users')

        # Deleting model 'ConfinePermission'
        db.delete_table('user_management_confinepermission')

        # Removing M2M table for field role on 'ConfinePermission'
        db.delete_table('user_management_confinepermission_role')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'user_management.activationrequest': {
            'Meta': {'object_name': 'ActivationRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'user_management.confinepermission': {
            'Meta': {'object_name': 'ConfinePermission'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'permission': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'role': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'permissions'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['user_management.Role']"})
        },
        'user_management.deleterequest': {
            'Meta': {'object_name': 'DeleteRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'user_management.researchgroup': {
            'Meta': {'object_name': 'ResearchGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'research_groups'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'user_management.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'research_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_management.ResearchGroup']"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['user_management']