# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Node'
        db.create_table('nodes_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('priv_ipv4_prefix', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True)),
            ('sliver_mac_prefix', self.gf('django.db.models.fields.PositiveSmallIntegerField')(max_length=16, null=True, blank=True)),
            ('sliver_pub_ipv4_total', self.gf('django.db.models.fields.IntegerField')()),
            ('cn_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('cndb_uri', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('cndb_cached_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('set_state', self.gf('django.db.models.fields.CharField')(default='install_conf', max_length=16)),
        ))
        db.send_create_signal('nodes', ['Node'])

        # Adding model 'NodeProp'
        db.create_table('nodes_nodeprop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('nodes', ['NodeProp'])

        # Adding model 'Host'
        db.create_table('nodes_host', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tinc_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('tinc_pubkey', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('nodes', ['Host'])

        # Adding M2M table for field connect_to on 'Host'
        db.create_table('nodes_host_connect_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('host', models.ForeignKey(orm['nodes.host'], null=False)),
            ('tincaddress', models.ForeignKey(orm['tinc.tincaddress'], null=False))
        ))
        db.create_unique('nodes_host_connect_to', ['host_id', 'tincaddress_id'])

        # Adding M2M table for field islands on 'Host'
        db.create_table('nodes_host_islands', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('host', models.ForeignKey(orm['nodes.host'], null=False)),
            ('island', models.ForeignKey(orm['tinc.island'], null=False))
        ))
        db.create_unique('nodes_host_islands', ['host_id', 'island_id'])

        # Adding model 'ResearchDevice'
        db.create_table('nodes_researchdevice', (
            ('tinc_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('tinc_pubkey', self.gf('django.db.models.fields.TextField')()),
            ('cn_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('cndb_uri', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('cndb_cached_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('uuid', self.gf('common.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('pubkey', self.gf('django.db.models.fields.TextField')()),
            ('cert', self.gf('django.db.models.fields.TextField')()),
            ('arch', self.gf('django.db.models.fields.CharField')(default='amd64', max_length=16)),
            ('boot_sn', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('local_iface', self.gf('django.db.models.fields.CharField')(default='eth0', max_length=16)),
        ))
        db.send_create_signal('nodes', ['ResearchDevice'])

        # Adding M2M table for field connect_to on 'ResearchDevice'
        db.create_table('nodes_researchdevice_connect_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('researchdevice', models.ForeignKey(orm['nodes.researchdevice'], null=False)),
            ('tincaddress', models.ForeignKey(orm['tinc.tincaddress'], null=False))
        ))
        db.create_unique('nodes_researchdevice_connect_to', ['researchdevice_id', 'tincaddress_id'])

        # Adding M2M table for field islands on 'ResearchDevice'
        db.create_table('nodes_researchdevice_islands', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('researchdevice', models.ForeignKey(orm['nodes.researchdevice'], null=False)),
            ('island', models.ForeignKey(orm['tinc.island'], null=False))
        ))
        db.create_unique('nodes_researchdevice_islands', ['researchdevice_id', 'island_id'])

        # Adding model 'RdDirectIface'
        db.create_table('nodes_rddirectiface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='eth0', max_length=16)),
            ('rd', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.ResearchDevice'])),
        ))
        db.send_create_signal('nodes', ['RdDirectIface'])

        # Adding model 'Server'
        db.create_table('nodes_server', (
            ('gateway_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tinc.Gateway'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['Server'])


    def backwards(self, orm):
        # Deleting model 'Node'
        db.delete_table('nodes_node')

        # Deleting model 'NodeProp'
        db.delete_table('nodes_nodeprop')

        # Deleting model 'Host'
        db.delete_table('nodes_host')

        # Removing M2M table for field connect_to on 'Host'
        db.delete_table('nodes_host_connect_to')

        # Removing M2M table for field islands on 'Host'
        db.delete_table('nodes_host_islands')

        # Deleting model 'ResearchDevice'
        db.delete_table('nodes_researchdevice')

        # Removing M2M table for field connect_to on 'ResearchDevice'
        db.delete_table('nodes_researchdevice_connect_to')

        # Removing M2M table for field islands on 'ResearchDevice'
        db.delete_table('nodes_researchdevice_islands')

        # Deleting model 'RdDirectIface'
        db.delete_table('nodes_rddirectiface')

        # Deleting model 'Server'
        db.delete_table('nodes_server')


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
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.Island']", 'symmetrical': 'False', 'blank': 'True'}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'nodes.rddirectiface': {
            'Meta': {'object_name': 'RdDirectIface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'rd': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.ResearchDevice']"})
        },
        'nodes.researchdevice': {
            'Meta': {'object_name': 'ResearchDevice'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'amd64'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cert': ('django.db.models.fields.TextField', [], {}),
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.Island']", 'symmetrical': 'False', 'blank': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {}),
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
            'tinc_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {})
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