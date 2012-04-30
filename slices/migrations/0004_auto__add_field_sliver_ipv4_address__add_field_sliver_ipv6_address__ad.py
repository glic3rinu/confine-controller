# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Sliver.ipv4_address'
        db.add_column('slices_sliver', 'ipv4_address',
                      self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Sliver.ipv6_address'
        db.add_column('slices_sliver', 'ipv6_address',
                      self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True),
                      keep_default=False)

        # Adding field 'NetworkRequest.mac_address'
        db.add_column('slices_networkrequest', 'mac_address',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=18, blank=True),
                      keep_default=False)

        # Adding field 'NetworkRequest.ipv4_address'
        db.add_column('slices_networkrequest', 'ipv4_address',
                      self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True),
                      keep_default=False)

        # Adding field 'NetworkRequest.ipv6_address'
        db.add_column('slices_networkrequest', 'ipv6_address',
                      self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39, null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Sliver.ipv4_address'
        db.delete_column('slices_sliver', 'ipv4_address')

        # Deleting field 'Sliver.ipv6_address'
        db.delete_column('slices_sliver', 'ipv6_address')

        # Deleting field 'NetworkRequest.mac_address'
        db.delete_column('slices_networkrequest', 'mac_address')

        # Deleting field 'NetworkRequest.ipv4_address'
        db.delete_column('slices_networkrequest', 'ipv4_address')

        # Deleting field 'NetworkRequest.ipv6_address'
        db.delete_column('slices_networkrequest', 'ipv6_address')

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
        'slices.cpurequest': {
            'Meta': {'object_name': 'CPURequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sliver': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.Sliver']", 'unique': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'weighted'", 'max_length': '16'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
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
            'ipv4_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'ipv6_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'mac_address': ('django.db.models.fields.CharField', [], {'max_length': '18', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '16'})
        },
        'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'code': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INSERTED'", 'max_length': '16'}),
            'template': ('django.db.models.fields.FilePathField', [], {'path': "'/home/controller/controller/media/templates'", 'max_length': '100', 'recursive': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'write_size': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'slices.sliver': {
            'Meta': {'unique_together': "(('slice', 'node'),)", 'object_name': 'Sliver'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipv4_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'ipv6_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Slice']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'INSERTED'", 'max_length': '16', 'blank': 'True'})
        },
        'slices.storagerequest': {
            'Meta': {'object_name': 'StorageRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'sliver': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['slices.Sliver']", 'unique': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'openwrt-backfire-amd64'", 'max_length': '128'})
        }
    }

    complete_apps = ['slices']