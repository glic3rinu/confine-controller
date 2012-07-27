# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Node.pubkey'
        db.delete_column('nodes_node', 'pubkey')

        # Deleting field 'Node.rd_boot_serial'
        db.delete_column('nodes_node', 'rd_boot_serial')

        # Deleting field 'Node.uuid'
        db.delete_column('nodes_node', 'uuid')

        # Adding field 'Node.rd_uuid'
        db.add_column('nodes_node', 'rd_uuid',
                      self.gf('django.db.models.fields.CharField')(default='1', unique=True, max_length=150),
                      keep_default=False)

        # Adding field 'Node.rd_pubkey'
        db.add_column('nodes_node', 'rd_pubkey',
                      self.gf('django.db.models.fields.TextField')(default='1'),
                      keep_default=False)

        # Adding field 'Node.rd_boot_sn'
        db.add_column('nodes_node', 'rd_boot_sn',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Deleting field 'TincHost.tinc_pubkey'
        db.delete_column('nodes_tinchost', 'tinc_pubkey')

        # Deleting field 'TincHost.tinc_name'
        db.delete_column('nodes_tinchost', 'tinc_name')

        # Adding field 'TincHost.name'
        db.add_column('nodes_tinchost', 'name',
                      self.gf('django.db.models.fields.CharField')(default='1', max_length=200),
                      keep_default=False)

        # Adding field 'TincHost.pubkey'
        db.add_column('nodes_tinchost', 'pubkey',
                      self.gf('django.db.models.fields.TextField')(default='1'),
                      keep_default=False)

        # Deleting field 'TincAddress.tinc_port'
        db.delete_column('nodes_tincaddress', 'tinc_port')

        # Deleting field 'TincAddress.tinc_ip'
        db.delete_column('nodes_tincaddress', 'tinc_ip')

        # Adding field 'TincAddress.ip_addr'
        db.add_column('nodes_tincaddress', 'ip_addr',
                      self.gf('django.db.models.fields.IPAddressField')(default='1.1.1.1', max_length=15),
                      keep_default=False)

        # Adding field 'TincAddress.port'
        db.add_column('nodes_tincaddress', 'port',
                      self.gf('django.db.models.fields.CharField')(default='1', max_length=10),
                      keep_default=False)

    def backwards(self, orm):
        # Adding field 'Node.pubkey'
        db.add_column('nodes_node', 'pubkey',
                      self.gf('django.db.models.fields.TextField')(default='AA'),
                      keep_default=False)

        # Adding field 'Node.rd_boot_serial'
        db.add_column('nodes_node', 'rd_boot_serial',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Node.uuid'
        db.add_column('nodes_node', 'uuid',
                      self.gf('django.db.models.fields.CharField')(default='1', max_length=150, unique=True),
                      keep_default=False)

        # Deleting field 'Node.rd_uuid'
        db.delete_column('nodes_node', 'rd_uuid')

        # Deleting field 'Node.rd_pubkey'
        db.delete_column('nodes_node', 'rd_pubkey')

        # Deleting field 'Node.rd_boot_sn'
        db.delete_column('nodes_node', 'rd_boot_sn')

        # Adding field 'TincHost.tinc_pubkey'
        db.add_column('nodes_tinchost', 'tinc_pubkey',
                      self.gf('django.db.models.fields.TextField')(default='1'),
                      keep_default=False)

        # Adding field 'TincHost.tinc_name'
        db.add_column('nodes_tinchost', 'tinc_name',
                      self.gf('django.db.models.fields.CharField')(default='1', max_length=200),
                      keep_default=False)

        # Deleting field 'TincHost.name'
        db.delete_column('nodes_tinchost', 'name')

        # Deleting field 'TincHost.pubkey'
        db.delete_column('nodes_tinchost', 'pubkey')

        # Adding field 'TincAddress.tinc_port'
        db.add_column('nodes_tincaddress', 'tinc_port',
                      self.gf('django.db.models.fields.CharField')(default='1', max_length=10),
                      keep_default=False)

        # Adding field 'TincAddress.tinc_ip'
        db.add_column('nodes_tincaddress', 'tinc_ip',
                      self.gf('django.db.models.fields.IPAddressField')(default='1.1.1.1', max_length=15),
                      keep_default=False)

        # Deleting field 'TincAddress.ip_addr'
        db.delete_column('nodes_tincaddress', 'ip_addr')

        # Deleting field 'TincAddress.port'
        db.delete_column('nodes_tincaddress', 'port')

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
            'rd_public_ipv4_avail': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rd_public_ipv4_total': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'rd_uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'sliver_mac_prefix': ('django.db.models.fields.CharField', [], {'default': "'0x200'", 'max_length': '50'}),
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