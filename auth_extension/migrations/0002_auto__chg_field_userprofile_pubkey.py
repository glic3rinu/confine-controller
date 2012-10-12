# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UserProfile.pubkey'
        db.alter_column('auth_extension_userprofile', 'pubkey', self.gf('django.db.models.fields.TextField')(unique=True, null=True))

    def backwards(self, orm):

        # Changing field 'UserProfile.pubkey'
        db.alter_column('auth_extension_userprofile', 'pubkey', self.gf('django.db.models.fields.TextField')(default='', unique=True))

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
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priv_ipv4_prefix': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'install_conf'", 'max_length': '16'}),
            'sliver_mac_prefix': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4_total': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'exp_data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
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
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'debian6'", 'max_length': '32'})
        }
    }

    complete_apps = ['auth_extension']