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
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=16)),
            ('code', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('slices', ['Slice'])

        # Adding model 'Sliver'
        db.create_table('slices_sliver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['slices.Slice'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='ONLINE', max_length=16)),
        ))
        db.send_create_signal('slices', ['Sliver'])

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
            ('type', self.gf('django.db.models.fields.CharField')(default='public', max_length=16)),
            ('min_rate', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('max_rate', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('max_throughput', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('slices', ['NetworkRequest'])

    def backwards(self, orm):
        # Deleting model 'Slice'
        db.delete_table('slices_slice')

        # Deleting model 'Sliver'
        db.delete_table('slices_sliver')

        # Deleting model 'MemoryRequest'
        db.delete_table('slices_memoryrequest')

        # Deleting model 'StorageRequest'
        db.delete_table('slices_storagerequest')

        # Deleting model 'CPURequest'
        db.delete_table('slices_cpurequest')

        # Deleting model 'NetworkRequest'
        db.delete_table('slices_networkrequest')

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
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'public_key': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '32'}),
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
            'max_rate': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'max_throughput': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'min_rate': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'sliver': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Sliver']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '16'})
        },
        'slices.slice': {
            'Meta': {'object_name': 'Slice'},
            'code': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'slices.sliver': {
            'Meta': {'object_name': 'Sliver'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'slice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['slices.Slice']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ONLINE'", 'max_length': '16'})
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