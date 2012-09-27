# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'ResearchDevice', fields ['pubkey']
        db.create_unique('nodes_researchdevice', ['pubkey'])

        # Adding unique constraint on 'ResearchDevice', fields ['tinc_pubkey']
        db.create_unique('nodes_researchdevice', ['tinc_pubkey'])

        # Adding unique constraint on 'ResearchDevice', fields ['cert']
        db.create_unique('nodes_researchdevice', ['cert'])

        # Adding unique constraint on 'ResearchDevice', fields ['tinc_name']
        db.create_unique('nodes_researchdevice', ['tinc_name'])

        # Adding unique constraint on 'Host', fields ['tinc_pubkey']
        db.create_unique('nodes_host', ['tinc_pubkey'])

        # Adding unique constraint on 'Host', fields ['tinc_name']
        db.create_unique('nodes_host', ['tinc_name'])

        # Adding unique constraint on 'NodeProp', fields ['name']
        db.create_unique('nodes_nodeprop', ['name'])

        # Adding unique constraint on 'RdDirectIface', fields ['rd', 'name']
        db.create_unique('nodes_rddirectiface', ['rd_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'RdDirectIface', fields ['rd', 'name']
        db.delete_unique('nodes_rddirectiface', ['rd_id', 'name'])

        # Removing unique constraint on 'NodeProp', fields ['name']
        db.delete_unique('nodes_nodeprop', ['name'])

        # Removing unique constraint on 'Host', fields ['tinc_name']
        db.delete_unique('nodes_host', ['tinc_name'])

        # Removing unique constraint on 'Host', fields ['tinc_pubkey']
        db.delete_unique('nodes_host', ['tinc_pubkey'])

        # Removing unique constraint on 'ResearchDevice', fields ['tinc_name']
        db.delete_unique('nodes_researchdevice', ['tinc_name'])

        # Removing unique constraint on 'ResearchDevice', fields ['cert']
        db.delete_unique('nodes_researchdevice', ['cert'])

        # Removing unique constraint on 'ResearchDevice', fields ['tinc_pubkey']
        db.delete_unique('nodes_researchdevice', ['tinc_pubkey'])

        # Removing unique constraint on 'ResearchDevice', fields ['pubkey']
        db.delete_unique('nodes_researchdevice', ['pubkey'])


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
        'nodes.host': {
            'Meta': {'object_name': 'Host'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.Island']", 'symmetrical': 'False', 'blank': 'True'}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
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
            'sliver_pub_ipv4_total': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.nodeprop': {
            'Meta': {'object_name': 'NodeProp'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'nodes.rddirectiface': {
            'Meta': {'unique_together': "(['name', 'rd'],)", 'object_name': 'RdDirectIface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'rd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.ResearchDevice']"})
        },
        'nodes.researchdevice': {
            'Meta': {'object_name': 'ResearchDevice'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'amd64'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cert': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.Island']", 'symmetrical': 'False', 'blank': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'uuid': ('common.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'nodes.server': {
            'Meta': {'object_name': 'Server', '_ormbases': ['tinc.Gateway']},
            'gateway_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tinc.Gateway']", 'unique': 'True', 'primary_key': 'True'})
        },
        'tinc.gateway': {
            'Meta': {'object_name': 'Gateway'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'tinc.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'tinc.tincaddress': {
            'Meta': {'object_name': 'TincAddress'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tinc.Island']"}),
            'port': ('django.db.models.fields.SmallIntegerField', [], {'default': "'666'"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tinc.Gateway']"})
        }
    }

    complete_apps = ['nodes']