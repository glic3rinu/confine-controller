# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Slice'
        db.create_table('slices_slice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.SliverTemplate'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('research_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user_management.ResearchGroup'], null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='INSERTED', max_length=16)),
            ('write_size', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('code', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('vlan_nr', self.gf('django.db.models.fields.IntegerField')()),
            ('exp_data_uri', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('exp_data_sha256', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('action', self.gf('django.db.models.fields.CharField')(default='INSERTED', max_length=16)),
        ))
        db.send_create_signal('slices', ['Slice'])

        # Adding model 'Sliver'
        db.create_table('slices_sliver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Slice'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('ipv4_address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
            ('ipv6_address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='INSERTED', max_length=16, blank=True)),
            ('nr', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal('slices', ['Sliver'])

        # Adding unique constraint on 'Sliver', fields ['slice', 'node']
        db.create_unique('slices_sliver', ['slice_id', 'node_id'])

        # Adding model 'SliverTemplate'
        db.create_table('slices_slivertemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('template_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('arch', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('data_uri', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('data_sha256', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('slices', ['SliverTemplate'])

        # Adding model 'MemoryRequest'
        db.create_table('slices_memoryrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.Sliver'], unique=True)),
            ('min', self.gf('django.db.models.fields.BigIntegerField')()),
            ('max', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal('slices', ['MemoryRequest'])

        # Adding model 'StorageRequest'
        db.create_table('slices_storagerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.Sliver'], unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='openwrt-backfire-amd64', max_length=128)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('slices', ['StorageRequest'])

        # Adding model 'CPURequest'
        db.create_table('slices_cpurequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.Sliver'], unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='weighted', max_length=16)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('slices', ['CPURequest'])

        # Adding model 'NetworkRequest'
        db.create_table('slices_networkrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('interface', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='network_requests', null=True, to=orm['nodes.Interface'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='public', max_length=16)),
            ('mac_address', self.gf('django.db.models.fields.CharField')(max_length=18, blank=True)),
            ('ipv4_address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
            ('ipv6_address', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
        ))
        db.send_create_signal('slices', ['NetworkRequest'])

        # Adding model 'SliverIface'
        db.create_table('slices_sliveriface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nr', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('mac_addr', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('slices', ['SliverIface'])

        # Adding model 'IsolatedIface'
        db.create_table('slices_isolatediface', (
            ('sliveriface_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.SliverIface'], unique=True, primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Interface'])),
        ))
        db.send_create_signal('slices', ['IsolatedIface'])

        # Adding model 'IpSliverIface'
        db.create_table('slices_ipsliveriface', (
            ('sliveriface_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.SliverIface'], unique=True, primary_key=True)),
            ('use_default_gw', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ipv6_addr', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
            ('ipv4_addr', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
        ))
        db.send_create_signal('slices', ['IpSliverIface'])

        # Adding model 'PublicIface'
        db.create_table('slices_publiciface', (
            ('ipsliveriface_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.IpSliverIface'], unique=True, primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('nr', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('slices', ['PublicIface'])

        # Adding model 'PrivateIface'
        db.create_table('slices_privateiface', (
            ('ipsliveriface_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.IpSliverIface'], unique=True, primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('nr', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('slices', ['PrivateIface'])

    def backwards(self, orm):
        # Removing unique constraint on 'Sliver', fields ['slice', 'node']
        db.delete_unique('slices_sliver', ['slice_id', 'node_id'])

        # Deleting model 'Slice'
        db.delete_table('slices_slice')

        # Deleting model 'Sliver'
        db.delete_table('slices_sliver')

        # Deleting model 'SliverTemplate'
        db.delete_table('slices_slivertemplate')

        # Deleting model 'MemoryRequest'
        db.delete_table('slices_memoryrequest')

        # Deleting model 'StorageRequest'
        db.delete_table('slices_storagerequest')

        # Deleting model 'CPURequest'
        db.delete_table('slices_cpurequest')

        # Deleting model 'NetworkRequest'
        db.delete_table('slices_networkrequest')

        # Deleting model 'SliverIface'
        db.delete_table('slices_sliveriface')

        # Deleting model 'IsolatedIface'
        db.delete_table('slices_isolatediface')

        # Deleting model 'IpSliverIface'
        db.delete_table('slices_ipsliveriface')

        # Deleting model 'PublicIface'
        db.delete_table('slices_publiciface')

        # Deleting model 'PrivateIface'
        db.delete_table('slices_privateiface')

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
        'slices.cpurequest': {
            'Meta': {'object_name': 'CPURequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sliver': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.Sliver']", 'unique': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'weighted'", 'max_length': '16'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'slices.ipsliveriface': {
            'Meta': {'object_name': 'IpSliverIface', '_ormbases': ['slices.SliverIface']},
            'ipv4_addr': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'ipv6_addr': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'sliveriface_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.SliverIface']", 'unique': 'True', 'primary_key': 'True'}),
            'use_default_gw': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'slices.isolatediface': {
            'Meta': {'object_name': 'IsolatedIface', '_ormbases': ['slices.SliverIface']},
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Interface']"}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"}),
            'sliveriface_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.SliverIface']", 'unique': 'True', 'primary_key': 'True'})
        },
        'slices.memoryrequest': {
            'Meta': {'object_name': 'MemoryRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.BigIntegerField', [], {}),
            'min': ('django.db.models.fields.BigIntegerField', [], {}),
            'sliver': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.Sliver']", 'unique': 'True'})
        },
        'slices.networkrequest': {
            'Meta': {'object_name': 'NetworkRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'network_requests'", 'null': 'True', 'to': "orm['nodes.Interface']"}),
            'ipv4_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'ipv6_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'max_length': '18', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '16'})
        },
        'slices.privateiface': {
            'Meta': {'object_name': 'PrivateIface', '_ormbases': ['slices.IpSliverIface']},
            'ipsliveriface_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.IpSliverIface']", 'unique': 'True', 'primary_key': 'True'}),
            'nr': ('django.db.models.fields.IntegerField', [], {}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"})
        },
        'slices.publiciface': {
            'Meta': {'object_name': 'PublicIface', '_ormbases': ['slices.IpSliverIface']},
            'ipsliveriface_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.IpSliverIface']", 'unique': 'True', 'primary_key': 'True'}),
            'nr': ('django.db.models.fields.IntegerField', [], {}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"})
        },
        'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'action': ('django.db.models.fields.CharField', [], {'default': "'INSERTED'", 'max_length': '16'}),
            'code': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'exp_data_sha256': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'exp_data_uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'research_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_management.ResearchGroup']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INSERTED'", 'max_length': '16'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.SliverTemplate']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'vlan_nr': ('django.db.models.fields.IntegerField', [], {}),
            'write_size': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'slices.sliver': {
            'Meta': {'unique_together': "(('slice', 'node'),)", 'object_name': 'Sliver'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipv4_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'ipv6_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'nr': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Slice']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INSERTED'", 'max_length': '16', 'blank': 'True'})
        },
        'slices.sliveriface': {
            'Meta': {'object_name': 'SliverIface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac_addr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'nr': ('django.db.models.fields.IntegerField', [], {})
        },
        'slices.slivertemplate': {
            'Meta': {'object_name': 'SliverTemplate'},
            'arch': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'data_sha256': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'data_uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'template_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'slices.storagerequest': {
            'Meta': {'object_name': 'StorageRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'sliver': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.Sliver']", 'unique': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'openwrt-backfire-amd64'", 'max_length': '128'})
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

    complete_apps = ['slices']