# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field connect_to on 'TincHost'
        db.create_table('nodes_tinchost_connect_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tinchost', models.ForeignKey(orm['nodes.tinchost'], null=False)),
            ('tincaddress', models.ForeignKey(orm['nodes.tincaddress'], null=False))
        ))
        db.create_unique('nodes_tinchost_connect_to', ['tinchost_id', 'tincaddress_id'])

    def backwards(self, orm):
        # Removing M2M table for field connect_to on 'TincHost'
        db.delete_table('nodes_tinchost_connect_to')

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
        'nodes.cpu': {
            'Meta': {'object_name': 'CPU'},
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'})
        },
        'nodes.deleterequest': {
            'Meta': {'object_name': 'DeleteRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"})
        },
        'nodes.gateway': {
            'Meta': {'object_name': 'Gateway', '_ormbases': ['nodes.TincServer']},
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'tincserver_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincServer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.host': {
            'Meta': {'object_name': 'Host', '_ormbases': ['nodes.TincClient']},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'tincclient_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincClient']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.interface': {
            'Meta': {'object_name': 'Interface'},
            'channel': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': "'150'", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'802.11a/b/g/n'", 'max_length': '255'})
        },
        'nodes.island': {
            'Meta': {'object_name': 'Island'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'nodes.memory': {
            'Meta': {'object_name': 'Memory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node', '_ormbases': ['nodes.TincClient']},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'priv_ipv4_prefix': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'rd_arch': ('django.db.models.fields.CharField', [], {'default': "'x86_generic'", 'max_length': '128'}),
            'rd_boot_sn': ('django.db.models.fields.IntegerField', [], {}),
            'rd_cert': ('django.db.models.fields.TextField', [], {}),
            'rd_pubkey': ('django.db.models.fields.TextField', [], {}),
            'rd_uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'sliver_mac_prefix': ('django.db.models.fields.CharField', [], {'default': "'0x200'", 'max_length': '50'}),
            'sliver_public_ipv4_avail': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sliver_public_ipv4_total': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'tincclient_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincClient']", 'unique': 'True', 'primary_key': 'True'}),
            'uci': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'nodes.nodeprops': {
            'Meta': {'object_name': 'NodeProps'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'nodes.storage': {
            'Meta': {'object_name': 'Storage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'types': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'nodes.tincaddress': {
            'Meta': {'object_name': 'TincAddress'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Island']"}),
            'port': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'nodes.tincclient': {
            'Meta': {'object_name': 'TincClient', '_ormbases': ['nodes.TincHost']},
            'island': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['nodes.Island']", 'symmetrical': 'False'}),
            'tinchost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincHost']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.tinchost': {
            'Meta': {'object_name': 'TincHost'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'host_connect_to'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['nodes.TincAddress']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pubkey': ('django.db.models.fields.TextField', [], {})
        },
        'nodes.tincserver': {
            'Meta': {'object_name': 'TincServer', '_ormbases': ['nodes.TincHost']},
            'tinc_address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.TincAddress']"}),
            'tinchost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincHost']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['nodes']