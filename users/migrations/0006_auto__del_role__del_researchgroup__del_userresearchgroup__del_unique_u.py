# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'UserResearchGroup', fields ['user', 'research_group']
        db.delete_unique(u'users_userresearchgroup', ['user_id', 'research_group_id'])

        # Deleting model 'Role'
        db.delete_table(u'users_role')

        # Removing M2M table for field permissions on 'Role'
        db.delete_table('users_role_permissions')

        # Deleting model 'ResearchGroup'
        db.delete_table(u'users_researchgroup')

        # Deleting model 'UserResearchGroup'
        db.delete_table(u'users_userresearchgroup')

        # Removing M2M table for field roles on 'UserResearchGroup'
        db.delete_table('users_userresearchgroup_roles')

        # Deleting model 'Permission'
        db.delete_table(u'users_permission')

        # Adding model 'Roles'
        db.create_table(u'users_roles', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Group'])),
            ('is_admin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_technician', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_researcher', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'users', ['Roles'])

        # Adding unique constraint on 'Roles', fields ['user', 'group']
        db.create_unique(u'users_roles', ['user_id', 'group_id'])

        # Adding model 'Group'
        db.create_table(u'users_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, unique=True, null=True, blank=True)),
            ('pubkey', self.gf('django.db.models.fields.TextField')(unique=True, null=True, blank=True)),
            ('allow_nodes', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_slices', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'users', ['Group'])

        # Deleting field 'User.phone'
        db.delete_column(u'users_user', 'phone')


    def backwards(self, orm):
        # Removing unique constraint on 'Roles', fields ['user', 'group']
        db.delete_unique(u'users_roles', ['user_id', 'group_id'])

        # Adding model 'Role'
        db.create_table(u'users_role', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'users', ['Role'])

        # Adding M2M table for field permissions on 'Role'
        db.create_table(u'users_role_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('role', models.ForeignKey(orm[u'users.role'], null=False)),
            ('permission', models.ForeignKey(orm[u'users.permission'], null=False))
        ))
        db.create_unique(u'users_role_permissions', ['role_id', 'permission_id'])

        # Adding model 'ResearchGroup'
        db.create_table(u'users_researchgroup', (
            ('city', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('postal_code', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=32)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32, unique=True)),
        ))
        db.send_create_signal(u'users', ['ResearchGroup'])

        # Adding model 'UserResearchGroup'
        db.create_table(u'users_userresearchgroup', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('research_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.ResearchGroup'])),
        ))
        db.send_create_signal(u'users', ['UserResearchGroup'])

        # Adding M2M table for field roles on 'UserResearchGroup'
        db.create_table(u'users_userresearchgroup_roles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userresearchgroup', models.ForeignKey(orm[u'users.userresearchgroup'], null=False)),
            ('role', models.ForeignKey(orm[u'users.role'], null=False))
        ))
        db.create_unique(u'users_userresearchgroup_roles', ['userresearchgroup_id', 'role_id'])

        # Adding unique constraint on 'UserResearchGroup', fields ['user', 'research_group']
        db.create_unique(u'users_userresearchgroup', ['user_id', 'research_group_id'])

        # Adding model 'Permission'
        db.create_table(u'users_permission', (
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='testbedpermission_set', to=orm['contenttypes.ContentType'])),
            ('eval_description', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('eval', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=16)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'users', ['Permission'])

        # Deleting model 'Roles'
        db.delete_table(u'users_roles')

        # Deleting model 'Group'
        db.delete_table(u'users_group')

        # Adding field 'User.phone'
        db.add_column(u'users_user', 'phone',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True),
                      keep_default=False)


    models = {
        u'users.authtoken': {
            'Meta': {'object_name': 'AuthToken'},
            'data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
        },
        u'users.group': {
            'Meta': {'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'users.roles': {
            'Meta': {'unique_together': "(('user', 'group'),)", 'object_name': 'Roles'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_researcher': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_technician': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
        },
        u'users.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.Group']", 'symmetrical': 'False', 'through': u"orm['users.Roles']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['users']