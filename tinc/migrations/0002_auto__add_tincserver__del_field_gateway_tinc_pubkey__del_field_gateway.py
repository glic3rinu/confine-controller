# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TincServer'
        db.create_table('tinc_tincserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tinc_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('tinc_pubkey', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('gateway', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['tinc.Gateway'], unique=True)),
        ))
        db.send_create_signal('tinc', ['TincServer'])

        # Adding M2M table for field connect_to on 'TincServer'
        db.create_table('tinc_tincserver_connect_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tincserver', models.ForeignKey(orm['tinc.tincserver'], null=False)),
            ('tincaddress', models.ForeignKey(orm['tinc.tincaddress'], null=False))
        ))
        db.create_unique('tinc_tincserver_connect_to', ['tincserver_id', 'tincaddress_id'])

        # Deleting field 'Gateway.tinc_pubkey'
        db.delete_column('tinc_gateway', 'tinc_pubkey')

        # Deleting field 'Gateway.tinc_name'
        db.delete_column('tinc_gateway', 'tinc_name')

        # Adding field 'Gateway.cn_url'
        db.add_column('tinc_gateway', 'cn_url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Gateway.cndb_uri'
        db.add_column('tinc_gateway', 'cndb_uri',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True),
                      keep_default=False)

        # Adding field 'Gateway.cndb_cached_on'
        db.add_column('tinc_gateway', 'cndb_cached_on',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field connect_to on 'Gateway'
        db.delete_table('tinc_gateway_connect_to')


        # Changing field 'TincAddress.server'
        db.alter_column('tinc_tincaddress', 'server_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tinc.TincServer']))

    def backwards(self, orm):
        # Deleting model 'TincServer'
        db.delete_table('tinc_tincserver')

        # Removing M2M table for field connect_to on 'TincServer'
        db.delete_table('tinc_tincserver_connect_to')

        # Adding field 'Gateway.tinc_pubkey'
        db.add_column('tinc_gateway', 'tinc_pubkey',
                      self.gf('django.db.models.fields.TextField')(default='', unique=True),
                      keep_default=False)

        # Adding field 'Gateway.tinc_name'
        db.add_column('tinc_gateway', 'tinc_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=64, unique=True),
                      keep_default=False)

        # Deleting field 'Gateway.cn_url'
        db.delete_column('tinc_gateway', 'cn_url')

        # Deleting field 'Gateway.cndb_uri'
        db.delete_column('tinc_gateway', 'cndb_uri')

        # Deleting field 'Gateway.cndb_cached_on'
        db.delete_column('tinc_gateway', 'cndb_cached_on')

        # Adding M2M table for field connect_to on 'Gateway'
        db.create_table('tinc_gateway_connect_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gateway', models.ForeignKey(orm['tinc.gateway'], null=False)),
            ('tincaddress', models.ForeignKey(orm['tinc.tincaddress'], null=False))
        ))
        db.create_unique('tinc_gateway_connect_to', ['gateway_id', 'tincaddress_id'])


        # Changing field 'TincAddress.server'
        db.alter_column('tinc_tincaddress', 'server_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tinc.Gateway']))

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
        'tinc.gateway': {
            'Meta': {'object_name': 'Gateway'},
            'cn_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'cndb_cached_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cndb_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'tinc.host': {
            'Meta': {'object_name': 'Host'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tinc.TincServer']"})
        },
        'tinc.tincclient': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincClient'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.Island']", 'symmetrical': 'False', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'tinc.tincserver': {
            'Meta': {'object_name': 'TincServer'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'gateway': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tinc.Gateway']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['tinc']