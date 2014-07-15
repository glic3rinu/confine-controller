# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    """Set node as primary key for NodeGeolocation"""

    def forwards(self, orm):
        # Deleting field 'NodeGeolocation.id'
        db.delete_column(u'gis_nodegeolocation', u'id')


        # Changing field 'NodeGeolocation.node'
        db.alter_column(u'gis_nodegeolocation', 'node_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, primary_key=True, to=orm['nodes.Node']))

    def backwards(self, orm):
        # South cannot handle this migration properly (see #407)
        # so we need to handle specifically for Postgresql

        # Adding field 'NodeGeolocation.id'
        #db.add_column(u'gis_nodegeolocation', u'id',
        #              self.gf('django.db.models.fields.AutoField')(primary_key=True),
        #              keep_default=False)
        db.execute("CREATE SEQUENCE gis_nodegeolocation_seq")
        db.execute("ALTER TABLE gis_nodegeolocation ADD COLUMN id integer NOT NULL DEFAULT nextval('gis_nodegeolocation_seq'::regclass)")
        db.execute("ALTER SEQUENCE gis_nodegeolocation_seq OWNED BY gis_nodegeolocation.id")


        # Changing field 'NodeGeolocation.node'
        db.alter_column(u'gis_nodegeolocation', 'node_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['nodes.Node']))

    models = {
        u'gis.nodegeolocation': {
            'Meta': {'object_name': 'NodeGeolocation'},
            'address': ('django_google_maps.fields.AddressField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'geolocation': ('django_google_maps.fields.GeoLocationField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'gis'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['nodes.Node']"})
        },
        u'nodes.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'i686'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'cert': ('controller.models.fields.NullableTextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Island']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priv_ipv4_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '19', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'debug'", 'max_length': '16'}),
            'sliver_mac_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4': ('django.db.models.fields.CharField', [], {'default': "'dhcp'", 'max_length': '8'}),
            'sliver_pub_ipv4_range': ('controller.models.fields.NullableCharField', [], {'default': "'#8'", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv6': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'})
        },
        u'users.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['gis']
