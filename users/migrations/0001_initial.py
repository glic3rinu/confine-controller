# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Permission'
        db.create_table(u'users_permission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='testbedpermission_set', to=orm['contenttypes.ContentType'])),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('evaluation', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'users', ['Permission'])

        # Adding model 'Role'
        db.create_table(u'users_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
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
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('postal_code', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'users', ['ResearchGroup'])

        # Adding model 'UserResearchGroup'
        db.create_table(u'users_userresearchgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('research_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.ResearchGroup'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Role'])),
        ))
        db.send_create_signal(u'users', ['UserResearchGroup'])

        # Adding model 'User'
        db.create_table(u'users_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('pubkey', self.gf('django.db.models.fields.TextField')(unique=True, null=True, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36, blank=True)),
        ))
        db.send_create_signal(u'users', ['User'])

        # Adding model 'AuthToken'
        db.create_table(u'users_authtoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'users', ['AuthToken'])


    def backwards(self, orm):
        # Deleting model 'Permission'
        db.delete_table(u'users_permission')

        # Deleting model 'Role'
        db.delete_table(u'users_role')

        # Removing M2M table for field permissions on 'Role'
        db.delete_table('users_role_permissions')

        # Deleting model 'ResearchGroup'
        db.delete_table(u'users_researchgroup')

        # Deleting model 'UserResearchGroup'
        db.delete_table(u'users_userresearchgroup')

        # Deleting model 'User'
        db.delete_table(u'users_user')

        # Deleting model 'AuthToken'
        db.delete_table(u'users_authtoken')


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
            'data': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
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
            'Meta': {'object_name': 'UserResearchGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'research_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.ResearchGroup']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"})
        }
    }

    complete_apps = ['users']