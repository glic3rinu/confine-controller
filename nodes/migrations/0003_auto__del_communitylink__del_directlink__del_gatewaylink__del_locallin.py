# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CommunityLink'
        db.delete_table('nodes_communitylink')

        # Deleting model 'DirectLink'
        db.delete_table('nodes_directlink')

        # Deleting model 'GatewayLink'
        db.delete_table('nodes_gatewaylink')

        # Deleting model 'LocalLink'
        db.delete_table('nodes_locallink')

        # Deleting model 'Link'
        db.delete_table('nodes_link')

        # Removing M2M table for field connected_to on 'Link'
        db.delete_table('nodes_link_connected_to')

        # Adding model 'Interface'
        db.create_table('nodes_interface', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('nodes', ['Interface'])

        # Deleting field 'Node.status'
        db.delete_column('nodes_node', 'status')

        # Adding field 'Node.state'
        db.add_column('nodes_node', 'state',
                      self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=32),
                      keep_default=False)

    def backwards(self, orm):
        # Adding model 'CommunityLink'
        db.create_table('nodes_communitylink', (
            ('link_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Link'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['CommunityLink'])

        # Adding model 'DirectLink'
        db.create_table('nodes_directlink', (
            ('link_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Link'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['DirectLink'])

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

        # Adding model 'Link'
        db.create_table('nodes_link', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=32)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['Link'])

        # Adding M2M table for field connected_to on 'Link'
        db.create_table('nodes_link_connected_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('link', models.ForeignKey(orm['nodes.link'], null=False)),
            ('node', models.ForeignKey(orm['nodes.node'], null=False))
        ))
        db.create_unique('nodes_link_connected_to', ['link_id', 'node_id'])

        # Deleting model 'Interface'
        db.delete_table('nodes_interface')

        # Adding field 'Node.status'
        db.add_column('nodes_node', 'status',
                      self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=32),
                      keep_default=False)

        # Deleting field 'Node.state'
        db.delete_column('nodes_node', 'state')

    models = {
        'nodes.cpu': {
            'Meta': {'object_name': 'CPU'},
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': "'1'"})
        },
        'nodes.deleterequest': {
            'Meta': {'object_name': 'DeleteRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"})
        },
        'nodes.interface': {
            'Meta': {'object_name': 'Interface'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'public_key': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
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