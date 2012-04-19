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
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('architecture', self.gf('django.db.models.fields.CharField')(default='x86_generic', max_length=128)),
            ('latitude', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('longitude', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('uci', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('public_key', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=32)),
        ))
        db.send_create_signal('nodes', ['Node'])

        # Adding model 'Storage'
        db.create_table('nodes_storage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('types', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('nodes', ['Storage'])

        # Adding model 'Memory'
        db.create_table('nodes_memory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('size', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
        ))
        db.send_create_signal('nodes', ['Memory'])

        # Adding model 'CPU'
        db.create_table('nodes_cpu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(default='1')),
            ('frequency', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal('nodes', ['CPU'])

        # Adding model 'Link'
        db.create_table('nodes_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=32)),
        ))
        db.send_create_signal('nodes', ['Link'])

        # Adding M2M table for field connected_to on 'Link'
        db.create_table('nodes_link_connected_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('link', models.ForeignKey(orm['nodes.link'], null=False)),
            ('node', models.ForeignKey(orm['nodes.node'], null=False))
        ))
        db.create_unique('nodes_link_connected_to', ['link_id', 'node_id'])

        # Adding model 'CommunityLink'
        db.create_table('nodes_communitylink', (
            ('link_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Link'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['CommunityLink'])

        # Adding model 'GatewayLink'
        db.create_table('nodes_gatewaylink', (
            ('link_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Link'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['GatewayLink'])

        # Adding model 'LocalLink'
        db.create_table('nodes_locallink', (
            ('link_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Link'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['LocalLink'])

        # Adding model 'DirectLink'
        db.create_table('nodes_directlink', (
            ('link_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Link'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['DirectLink'])

    def backwards(self, orm):
        # Deleting model 'Node'
        db.delete_table('nodes_node')

        # Deleting model 'Storage'
        db.delete_table('nodes_storage')

        # Deleting model 'Memory'
        db.delete_table('nodes_memory')

        # Deleting model 'CPU'
        db.delete_table('nodes_cpu')

        # Deleting model 'Link'
        db.delete_table('nodes_link')

        # Removing M2M table for field connected_to on 'Link'
        db.delete_table('nodes_link_connected_to')

        # Deleting model 'CommunityLink'
        db.delete_table('nodes_communitylink')

        # Deleting model 'GatewayLink'
        db.delete_table('nodes_gatewaylink')

        # Deleting model 'LocalLink'
        db.delete_table('nodes_locallink')

        # Deleting model 'DirectLink'
        db.delete_table('nodes_directlink')

    models = {
        'nodes.communitylink': {
            'Meta': {'object_name': 'CommunityLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.cpu': {
            'Meta': {'object_name': 'CPU'},
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': "'1'"})
        },
        'nodes.directlink': {
            'Meta': {'object_name': 'DirectLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.gatewaylink': {
            'Meta': {'object_name': 'GatewayLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.link': {
            'Meta': {'object_name': 'Link'},
            'connected_to': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'connected_to'", 'blank': 'True', 'to': "orm['nodes.Node']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'})
        },
        'nodes.locallink': {
            'Meta': {'object_name': 'LocalLink', '_ormbases': ['nodes.Link']},
            'link_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Link']", 'unique': 'True', 'primary_key': 'True'})
        },
        'nodes.memory': {
            'Meta': {'object_name': 'Memory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'architecture': ('django.db.models.fields.CharField', [], {'default': "'x86_generic'", 'max_length': '128'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'public_key': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
            'uci': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'nodes.storage': {
            'Meta': {'object_name': 'Storage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'types': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['nodes']