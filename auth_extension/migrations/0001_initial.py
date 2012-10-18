# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ResearchGroup'
        db.create_table('auth_extension_researchgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('auth_extension', ['ResearchGroup'])

        # Adding model 'AuthorizedOfficial'
        db.create_table('auth_extension_authorizedofficial', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('research_group', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth_extension.ResearchGroup'], unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('second_surname', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('national_id', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default='Barcelona', max_length=20, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('province', self.gf('django.db.models.fields.CharField')(default='Barcelona', max_length=20, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(default='Spain', max_length=20)),
        ))
        db.send_create_signal('auth_extension', ['AuthorizedOfficial'])

        # Adding model 'UserProfile'
        db.create_table('auth_extension_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pubkey', self.gf('django.db.models.fields.TextField')(unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('auth_extension', ['UserProfile'])

        # Adding M2M table for field research_groups on 'UserProfile'
        db.create_table('auth_extension_userprofile_research_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['auth_extension.userprofile'], null=False)),
            ('researchgroup', models.ForeignKey(orm['auth_extension.researchgroup'], null=False))
        ))
        db.create_unique('auth_extension_userprofile_research_groups', ['userprofile_id', 'researchgroup_id'])

        # Adding model 'TestbedPermission'
        db.create_table('auth_extension_testbedpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('common.fields.MultiSelectField')(max_length=250, blank=True)),
            ('research_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth_extension.ResearchGroup'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Slice'], null=True, blank=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'], null=True, blank=True)),
        ))
        db.send_create_signal('auth_extension', ['TestbedPermission'])

        # Adding model 'AuthToken'
        db.create_table('auth_extension_authtoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('auth_extension', ['AuthToken'])


    def backwards(self, orm):
        # Deleting model 'ResearchGroup'
        db.delete_table('auth_extension_researchgroup')

        # Deleting model 'AuthorizedOfficial'
        db.delete_table('auth_extension_authorizedofficial')

        # Deleting model 'UserProfile'
        db.delete_table('auth_extension_userprofile')

        # Removing M2M table for field research_groups on 'UserProfile'
        db.delete_table('auth_extension_userprofile_research_groups')

        # Deleting model 'TestbedPermission'
        db.delete_table('auth_extension_testbedpermission')

        # Deleting model 'AuthToken'
        db.delete_table('auth_extension_authtoken')


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
        'auth_extension.authorizedofficial': {
            'Meta': {'object_name': 'AuthorizedOfficial'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "'Barcelona'", 'max_length': '20', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'Spain'", 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'national_id': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'province': ('django.db.models.fields.CharField', [], {'default': "'Barcelona'", 'max_length': '20', 'blank': 'True'}),
            'research_group': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth_extension.ResearchGroup']", 'unique': 'True'}),
            'second_surname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'auth_extension.authtoken': {
            'Meta': {'object_name': 'AuthToken'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'auth_extension.researchgroup': {
            'Meta': {'object_name': 'ResearchGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'auth_extension.testbedpermission': {
            'Meta': {'object_name': 'TestbedPermission'},
            'action': ('common.fields.MultiSelectField', [], {'max_length': '250', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']", 'null': 'True', 'blank': 'True'}),
            'research_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth_extension.ResearchGroup']", 'null': 'True', 'blank': 'True'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Slice']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'auth_extension.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'research_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth_extension.ResearchGroup']", 'symmetrical': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'arch': ('django.db.models.fields.CharField', [], {'default': "'x86_64'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'cert': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'priv_ipv4_prefix': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'install_conf'", 'max_length': '16'}),
            'sliver_mac_prefix': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4_total': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'exp_data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 17, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'new_sliver_instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'register'", 'max_length': '16'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Template']"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36', 'blank': 'True'}),
            'vlan_nr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'slices.template': {
            'Meta': {'object_name': 'Template'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'amd64'", 'max_length': '32'}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'debian6'", 'max_length': '32'})
        },
        'tinc.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'tinc.tincaddress': {
            'Meta': {'object_name': 'TincAddress'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tinc.Island']"}),
            'port': ('django.db.models.fields.SmallIntegerField', [], {'default': "'666'"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tinc.TincServer']"})
        },
        'tinc.tincclient': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincClient'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tinc.Island']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '36'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'tinc.tincserver': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincServer'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '36'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['auth_extension']