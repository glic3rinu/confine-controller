# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("nodes", "0001_initial"),
    )


    def forwards(self, orm):
        # Adding model 'Template'
        db.create_table('slices_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='debian6', max_length=32)),
            ('arch', self.gf('django.db.models.fields.CharField')(default='amd64', max_length=32)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('data', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('slices', ['Template'])

        # Adding model 'Slice'
        db.create_table('slices_slice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36, blank=True)),
            ('pubkey', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('expires_on', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 17, 0, 0), null=True, blank=True)),
            ('instance_sn', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('new_sliver_instance_sn', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('vlan_nr', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('exp_data', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('set_state', self.gf('django.db.models.fields.CharField')(default='register', max_length=16)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Template'])),
        ))
        db.send_create_signal('slices', ['Slice'])

        # Adding M2M table for field users on 'Slice'
        db.create_table('slices_slice_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('slice', models.ForeignKey(orm['slices.slice'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('slices_slice_users', ['slice_id', 'user_id'])

        # Adding model 'SliceProp'
        db.create_table('slices_sliceprop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Slice'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('slices', ['SliceProp'])

        # Adding unique constraint on 'SliceProp', fields ['slice', 'name']
        db.create_unique('slices_sliceprop', ['slice_id', 'name'])

        # Adding model 'Sliver'
        db.create_table('slices_sliver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('instance_sn', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Slice'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
        ))
        db.send_create_signal('slices', ['Sliver'])

        # Adding model 'SliverProp'
        db.create_table('slices_sliverprop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('slices', ['SliverProp'])

        # Adding unique constraint on 'SliverProp', fields ['sliver', 'name']
        db.create_unique('slices_sliverprop', ['sliver_id', 'name'])

        # Adding model 'IsolatedIface'
        db.create_table('slices_isolatediface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.DirectIface'], null=True, blank=True)),
        ))
        db.send_create_signal('slices', ['IsolatedIface'])

        # Adding unique constraint on 'IsolatedIface', fields ['sliver', 'parent']
        db.create_unique('slices_isolatediface', ['sliver_id', 'parent_id'])

        # Adding model 'PublicIface'
        db.create_table('slices_publiciface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('use_default_gw', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sliver', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Sliver'])),
        ))
        db.send_create_signal('slices', ['PublicIface'])

        # Adding model 'PrivateIface'
        db.create_table('slices_privateiface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('use_default_gw', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sliver', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['slices.Sliver'], unique=True)),
        ))
        db.send_create_signal('slices', ['PrivateIface'])


    def backwards(self, orm):
        # Removing unique constraint on 'IsolatedIface', fields ['sliver', 'parent']
        db.delete_unique('slices_isolatediface', ['sliver_id', 'parent_id'])

        # Removing unique constraint on 'SliverProp', fields ['sliver', 'name']
        db.delete_unique('slices_sliverprop', ['sliver_id', 'name'])

        # Removing unique constraint on 'SliceProp', fields ['slice', 'name']
        db.delete_unique('slices_sliceprop', ['slice_id', 'name'])

        # Deleting model 'Template'
        db.delete_table('slices_template')

        # Deleting model 'Slice'
        db.delete_table('slices_slice')

        # Removing M2M table for field users on 'Slice'
        db.delete_table('slices_slice_users')

        # Deleting model 'SliceProp'
        db.delete_table('slices_sliceprop')

        # Deleting model 'Sliver'
        db.delete_table('slices_sliver')

        # Deleting model 'SliverProp'
        db.delete_table('slices_sliverprop')

        # Deleting model 'IsolatedIface'
        db.delete_table('slices_isolatediface')

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
        'nodes.directiface': {
            'Meta': {'unique_together': "(['name', 'node'],)", 'object_name': 'DirectIface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"})
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
        'slices.isolatediface': {
            'Meta': {'unique_together': "(['sliver', 'parent'],)", 'object_name': 'IsolatedIface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.DirectIface']", 'null': 'True', 'blank': 'True'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"})
        },
        'slices.privateiface': {
            'Meta': {'object_name': 'PrivateIface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'sliver': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.Sliver']", 'unique': 'True'}),
            'use_default_gw': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'slices.publiciface': {
            'Meta': {'object_name': 'PublicIface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"}),
            'use_default_gw': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
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
        'slices.sliceprop': {
            'Meta': {'unique_together': "(('slice', 'name'),)", 'object_name': 'SliceProp'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Slice']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'slices.sliver': {
            'Meta': {'object_name': 'Sliver'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_sn': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Slice']"})
        },
        'slices.sliverprop': {
            'Meta': {'unique_together': "(('sliver', 'name'),)", 'object_name': 'SliverProp'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
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

    complete_apps = ['slices']
