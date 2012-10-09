# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Host'
        db.create_table('tinc_host', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('tinc', ['Host'])

        # Adding model 'Gateway'
        db.create_table('tinc_gateway', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cn_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('cndb_uri', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('cndb_cached_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('tinc', ['Gateway'])

        # Adding model 'TincServer'
        db.create_table('tinc_tincserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pubkey', self.gf('django.db.models.fields.TextField')(unique=True)),
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

        # Adding model 'Island'
        db.create_table('tinc_island', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('tinc', ['Island'])

        # Adding model 'TincAddress'
        db.create_table('tinc_tincaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_addr', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39)),
            ('port', self.gf('django.db.models.fields.SmallIntegerField')(default='666')),
            ('island', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tinc.Island'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tinc.TincServer'])),
        ))
        db.send_create_signal('tinc', ['TincAddress'])

        # Adding model 'TincClient'
        db.create_table('tinc_tincclient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pubkey', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('tinc', ['TincClient'])

        # Adding unique constraint on 'TincClient', fields ['content_type', 'object_id']
        db.create_unique('tinc_tincclient', ['content_type_id', 'object_id'])

        # Adding M2M table for field connect_to on 'TincClient'
        db.create_table('tinc_tincclient_connect_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tincclient', models.ForeignKey(orm['tinc.tincclient'], null=False)),
            ('tincaddress', models.ForeignKey(orm['tinc.tincaddress'], null=False))
        ))
        db.create_unique('tinc_tincclient_connect_to', ['tincclient_id', 'tincaddress_id'])

        # Adding M2M table for field islands on 'TincClient'
        db.create_table('tinc_tincclient_islands', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tincclient', models.ForeignKey(orm['tinc.tincclient'], null=False)),
            ('island', models.ForeignKey(orm['tinc.island'], null=False))
        ))
        db.create_unique('tinc_tincclient_islands', ['tincclient_id', 'island_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'TincClient', fields ['content_type', 'object_id']
        db.delete_unique('tinc_tincclient', ['content_type_id', 'object_id'])

        # Deleting model 'Host'
        db.delete_table('tinc_host')

        # Deleting model 'Gateway'
        db.delete_table('tinc_gateway')

        # Deleting model 'TincServer'
        db.delete_table('tinc_tincserver')

        # Removing M2M table for field connect_to on 'TincServer'
        db.delete_table('tinc_tincserver_connect_to')

        # Deleting model 'Island'
        db.delete_table('tinc_island')

        # Deleting model 'TincAddress'
        db.delete_table('tinc_tincaddress')

        # Deleting model 'TincClient'
        db.delete_table('tinc_tincclient')

        # Removing M2M table for field connect_to on 'TincClient'
        db.delete_table('tinc_tincclient_connect_to')

        # Removing M2M table for field islands on 'TincClient'
        db.delete_table('tinc_tincclient_islands')


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
            'islands': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.Island']", 'symmetrical': 'False', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        },
        'tinc.tincserver': {
            'Meta': {'object_name': 'TincServer'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'gateway': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['tinc.Gateway']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['tinc']