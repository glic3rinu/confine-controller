# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Island'
        db.create_table('nodes_island', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('nodes', ['Island'])

        # Adding model 'TincAddress'
        db.create_table('nodes_tincaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('island', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Island'])),
            ('tinc_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('tinc_port', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('nodes', ['TincAddress'])

        # Adding model 'TincHost'
        db.create_table('nodes_tinchost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tinc_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tinc_pubkey', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('nodes', ['TincHost'])

        # Adding model 'TincClient'
        db.create_table('nodes_tincclient', (
            ('tinchost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.TincHost'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['TincClient'])

        # Adding M2M table for field island on 'TincClient'
        db.create_table('nodes_tincclient_island', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tincclient', models.ForeignKey(orm['nodes.tincclient'], null=False)),
            ('island', models.ForeignKey(orm['nodes.island'], null=False))
        ))
        db.create_unique('nodes_tincclient_island', ['tincclient_id', 'island_id'])

        # Adding model 'TincServer'
        db.create_table('nodes_tincserver', (
            ('tinchost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.TincHost'], unique=True, primary_key=True)),
            ('tinc_address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.TincAddress'])),
        ))
        db.send_create_signal('nodes', ['TincServer'])

        # Adding model 'Gateway'
        db.create_table('nodes_gateway', (
            ('tincserver_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.TincServer'], unique=True, primary_key=True)),
            ('cn_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('nodes', ['Gateway'])

        # Adding model 'Host'
        db.create_table('nodes_host', (
            ('tincclient_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.TincClient'], unique=True, primary_key=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('nodes', ['Host'])

        # Adding model 'Node'
        db.create_table('nodes_node', (
            ('tincclient_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.TincClient'], unique=True, primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('cn_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('rd_arch', self.gf('django.db.models.fields.CharField')(default='x86_generic', max_length=128)),
            ('latitude', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('longitude', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('uci', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('action', self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=32)),
            ('rd_public_ipv4_total', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('priv_ipv4_prefix', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('sliver_mac_prefix', self.gf('django.db.models.fields.CharField')(default='0x200', max_length=50)),
            ('state', self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=32)),
            ('rd_public_ipv4_avail', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodes', ['Node'])

        # Adding model 'DeleteRequest'
        db.create_table('nodes_deleterequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
        ))
        db.send_create_signal('nodes', ['DeleteRequest'])

        # Adding model 'Storage'
        db.create_table('nodes_storage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('types', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodes', ['Storage'])

        # Adding model 'Memory'
        db.create_table('nodes_memory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('size', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('nodes', ['Memory'])

        # Adding model 'CPU'
        db.create_table('nodes_cpu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(default='1', null=True, blank=True)),
            ('frequency', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
        ))
        db.send_create_signal('nodes', ['CPU'])

        # Adding model 'Interface'
        db.create_table('nodes_interface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('type', self.gf('django.db.models.fields.CharField')(default='802.11a/b/g/n', max_length=255)),
            ('channel', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('essid', self.gf('django.db.models.fields.CharField')(max_length='150', null=True, blank=True)),
        ))
        db.send_create_signal('nodes', ['Interface'])

    def backwards(self, orm):
        # Deleting model 'Island'
        db.delete_table('nodes_island')

        # Deleting model 'TincAddress'
        db.delete_table('nodes_tincaddress')

        # Deleting model 'TincHost'
        db.delete_table('nodes_tinchost')

        # Deleting model 'TincClient'
        db.delete_table('nodes_tincclient')

        # Removing M2M table for field island on 'TincClient'
        db.delete_table('nodes_tincclient_island')

        # Deleting model 'TincServer'
        db.delete_table('nodes_tincserver')

        # Deleting model 'Gateway'
        db.delete_table('nodes_gateway')

        # Deleting model 'Host'
        db.delete_table('nodes_host')

        # Deleting model 'Node'
        db.delete_table('nodes_node')

        # Deleting model 'DeleteRequest'
        db.delete_table('nodes_deleterequest')

        # Deleting model 'Storage'
        db.delete_table('nodes_storage')

        # Deleting model 'Memory'
        db.delete_table('nodes_memory')

        # Deleting model 'CPU'
        db.delete_table('nodes_cpu')

        # Deleting model 'Interface'
        db.delete_table('nodes_interface')

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
            'action': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'priv_ipv4_prefix': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'rd_arch': ('django.db.models.fields.CharField', [], {'default': "'x86_generic'", 'max_length': '128'}),
            'rd_public_ipv4_avail': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rd_public_ipv4_total': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sliver_mac_prefix': ('django.db.models.fields.CharField', [], {'default': "'0x200'", 'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'tincclient_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincClient']", 'unique': 'True', 'primary_key': 'True'}),
            'uci': ('django.db.models.fields.TextField', [], {'blank': 'True'})
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
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Island']"}),
            'tinc_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'tinc_port': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'nodes.tincclient': {
            'Meta': {'object_name': 'TincClient', '_ormbases': ['nodes.TincHost']},
            'island': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['nodes.Island']", 'symmetrical': 'False'}),
            'tinchost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincHost']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.tinchost': {
            'Meta': {'object_name': 'TincHost'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {})
        },
        'nodes.tincserver': {
            'Meta': {'object_name': 'TincServer', '_ormbases': ['nodes.TincHost']},
            'tinc_address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.TincAddress']"}),
            'tinchost_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.TincHost']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['nodes']