# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Template'
        db.create_table(u'slices_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='debian6', max_length=32)),
            ('arch', self.gf('django.db.models.fields.CharField')(default='amd64', max_length=32)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'slices', ['Template'])

        # Adding model 'Slice'
        db.create_table(u'slices_slice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36, blank=True)),
            ('pubkey', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('expires_on', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 27, 0, 0), null=True, blank=True)),
            ('instance_sn', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('new_sliver_instance_sn', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('vlan_nr', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('exp_data', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('set_state', self.gf('django.db.models.fields.CharField')(default='register', max_length=16)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Template'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Group'])),
        ))
        db.send_create_signal(u'slices', ['Slice'])

        # Adding model 'SliceProp'
        db.create_table(u'slices_sliceprop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Slice'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'slices', ['SliceProp'])

        # Adding unique constraint on 'SliceProp', fields ['slice', 'name']
        db.create_unique(u'slices_sliceprop', ['slice_id', 'name'])

        # Adding model 'Sliver'
        db.create_table(u'slices_sliver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Slice'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('instance_sn', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('exp_data', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Template'], null=True, blank=True)),
        ))
        db.send_create_signal(u'slices', ['Sliver'])

        # Adding unique constraint on 'Sliver', fields ['slice', 'node']
        db.create_unique(u'slices_sliver', ['slice_id', 'node_id'])

        # Adding model 'SliverProp'
        db.create_table(u'slices_sliverprop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'slices', ['SliverProp'])

        # Adding unique constraint on 'SliverProp', fields ['sliver', 'name']
        db.create_unique(u'slices_sliverprop', ['sliver_id', 'name'])

        # Adding model 'IsolatedIface'
        db.create_table(u'slices_isolatediface', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.DirectIface'], unique=True)),
        ))
        db.send_create_signal(u'slices', ['IsolatedIface'])

        # Adding model 'MgmtIface'
        db.create_table(u'slices_mgmtiface', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
        ))
        db.send_create_signal(u'slices', ['MgmtIface'])

        # Adding model 'Pub6Iface'
        db.create_table(u'slices_pub6iface', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
        ))
        db.send_create_signal(u'slices', ['Pub6Iface'])

        # Adding model 'Pub4Iface'
        db.create_table(u'slices_pub4iface', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
        ))
        db.send_create_signal(u'slices', ['Pub4Iface'])

        # Adding model 'PrivateIface'
        db.create_table(u'slices_privateiface', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sliver', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.Sliver'], unique=True)),
        ))
        db.send_create_signal(u'slices', ['PrivateIface'])


    def backwards(self, orm):
        # Removing unique constraint on 'SliverProp', fields ['sliver', 'name']
        db.delete_unique(u'slices_sliverprop', ['sliver_id', 'name'])

        # Removing unique constraint on 'Sliver', fields ['slice', 'node']
        db.delete_unique(u'slices_sliver', ['slice_id', 'node_id'])

        # Removing unique constraint on 'SliceProp', fields ['slice', 'name']
        db.delete_unique(u'slices_sliceprop', ['slice_id', 'name'])

        # Deleting model 'Template'
        db.delete_table(u'slices_template')

        # Deleting model 'Slice'
        db.delete_table(u'slices_slice')

        # Deleting model 'SliceProp'
        db.delete_table(u'slices_sliceprop')

        # Deleting model 'Sliver'
        db.delete_table(u'slices_sliver')

        # Deleting model 'SliverProp'
        db.delete_table(u'slices_sliverprop')

        # Deleting model 'IsolatedIface'
        db.delete_table(u'slices_isolatediface')

        # Deleting model 'MgmtIface'
        db.delete_table(u'slices_mgmtiface')

        # Deleting model 'Pub6Iface'
        db.delete_table(u'slices_pub6iface')

        # Deleting model 'Pub4Iface'
        db.delete_table(u'slices_pub4iface')

        # Deleting model 'PrivateIface'
        db.delete_table(u'slices_privateiface')


    models = {
        u'communitynetworks.cnhost': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'CnHost'},
            'app_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '36'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'nodes.directiface': {
            'Meta': {'unique_together': "(['name', 'node'],)", 'object_name': 'DirectIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Node']"})
        },
        u'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'x86_64'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'cert': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priv_ipv4_prefix': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'install_conf'", 'max_length': '16'}),
            'sliver_mac_prefix': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'}),
            'sliver_pub_ipv4_range': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv6': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'slices.isolatediface': {
            'Meta': {'object_name': 'IsolatedIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.DirectIface']", 'unique': 'True'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Sliver']"})
        },
        u'slices.mgmtiface': {
            'Meta': {'object_name': 'MgmtIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Sliver']"})
        },
        u'slices.privateiface': {
            'Meta': {'object_name': 'PrivateIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'sliver': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['slices.Sliver']", 'unique': 'True'})
        },
        u'slices.pub4iface': {
            'Meta': {'object_name': 'Pub4Iface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Sliver']"})
        },
        u'slices.pub6iface': {
            'Meta': {'object_name': 'Pub6Iface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Sliver']"})
        },
        u'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'exp_data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 27, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'new_sliver_instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'register'", 'max_length': '16'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Template']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36', 'blank': 'True'}),
            'vlan_nr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'slices.sliceprop': {
            'Meta': {'unique_together': "(('slice', 'name'),)", 'object_name': 'SliceProp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Slice']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'slices.sliver': {
            'Meta': {'unique_together': "(('slice', 'node'),)", 'object_name': 'Sliver'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'exp_data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Node']"}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Slice']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Template']", 'null': 'True', 'blank': 'True'})
        },
        u'slices.sliverprop': {
            'Meta': {'unique_together': "(('sliver', 'name'),)", 'object_name': 'SliverProp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['slices.Sliver']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'slices.template': {
            'Meta': {'object_name': 'Template'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'amd64'", 'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'debian6'", 'max_length': '32'})
        },
        u'tinc.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'tinc.tincaddress': {
            'Meta': {'object_name': 'TincAddress'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']"}),
            'port': ('django.db.models.fields.SmallIntegerField', [], {'default': "'666'"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.TincServer']"})
        },
        u'tinc.tincclient': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincClient'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '36'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        u'tinc.tincserver': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincServer'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '36'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        u'users.group': {
            'Meta': {'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['slices']