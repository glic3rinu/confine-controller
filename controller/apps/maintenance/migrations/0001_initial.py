# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Operation'
        db.create_table(u'maintenance_operation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('script', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'maintenance', ['Operation'])

        # Adding model 'Execution'
        db.create_table(u'maintenance_execution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('operation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='executions', to=orm['maintenance.Operation'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('script', self.gf('django.db.models.fields.TextField')()),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('include_new_nodes', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'maintenance', ['Execution'])

        # Adding model 'Instance'
        db.create_table(u'maintenance_instance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('execution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='instances', to=orm['maintenance.Execution'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='operations', to=orm['nodes.Node'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='RECEIVED', max_length=16)),
            ('last_try', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('stdout', self.gf('django.db.models.fields.TextField')()),
            ('stderr', self.gf('django.db.models.fields.TextField')()),
            ('traceback', self.gf('django.db.models.fields.TextField')()),
            ('exit_code', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal(u'maintenance', ['Instance'])


    def backwards(self, orm):
        # Deleting model 'Operation'
        db.delete_table(u'maintenance_operation')

        # Deleting model 'Execution'
        db.delete_table(u'maintenance_execution')

        # Deleting model 'Instance'
        db.delete_table(u'maintenance_instance')


    models = {
        u'communitynetworks.cnhost': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'CnHost'},
            'app_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('controller.models.fields.URIField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'maintenance.execution': {
            'Meta': {'ordering': "['-created_on']", 'object_name': 'Execution'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_new_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'operation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'executions'", 'to': u"orm['maintenance.Operation']"}),
            'script': ('django.db.models.fields.TextField', [], {})
        },
        u'maintenance.instance': {
            'Meta': {'object_name': 'Instance'},
            'execution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instances'", 'to': u"orm['maintenance.Execution']"}),
            'exit_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_try': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'operations'", 'to': u"orm['nodes.Node']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'RECEIVED'", 'max_length': '16'}),
            'stderr': ('django.db.models.fields.TextField', [], {}),
            'stdout': ('django.db.models.fields.TextField', [], {}),
            'traceback': ('django.db.models.fields.TextField', [], {})
        },
        u'maintenance.operation': {
            'Meta': {'object_name': 'Operation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'script': ('django.db.models.fields.TextField', [], {})
        },
        u'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'i686'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'cert': ('controller.models.fields.NullableTextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priv_ipv4_prefix': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'debug'", 'max_length': '16'}),
            'sliver_mac_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4': ('django.db.models.fields.CharField', [], {'default': "'dhcp'", 'max_length': '8'}),
            'sliver_pub_ipv4_range': ('controller.models.fields.NullableCharField', [], {'default': "'#8'", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv6': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'})
        },
        u'pings.ping': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'Ping'},
            'avg': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'mdev': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'min': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '9', 'decimal_places': '3'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'packet_loss': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'tinc.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'tinc.tincclient': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincClient'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']", 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'pubkey': ('controller.models.fields.RSAPublicKeyField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'users.group': {
            'Meta': {'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['maintenance']