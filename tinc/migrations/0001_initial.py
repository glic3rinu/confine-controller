# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gateway'
        db.create_table('tinc_gateway', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tinc_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('tinc_pubkey', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('tinc', ['Gateway'])

        # Adding M2M table for field connect_to on 'Gateway'
        db.create_table('tinc_gateway_connect_to', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gateway', models.ForeignKey(orm['tinc.gateway'], null=False)),
            ('tincaddress', models.ForeignKey(orm['tinc.tincaddress'], null=False))
        ))
        db.create_unique('tinc_gateway_connect_to', ['gateway_id', 'tincaddress_id'])

        # Adding model 'Island'
        db.create_table('tinc_island', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('tinc', ['Island'])

        # Adding model 'TincAddress'
        db.create_table('tinc_tincaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_addr', self.gf('django.db.models.fields.GenericIPAddressField')(max_length=39)),
            ('port', self.gf('django.db.models.fields.SmallIntegerField')(default='666')),
            ('island', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tinc.Island'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tinc.Gateway'])),
        ))
        db.send_create_signal('tinc', ['TincAddress'])


    def backwards(self, orm):
        # Deleting model 'Gateway'
        db.delete_table('tinc_gateway')

        # Removing M2M table for field connect_to on 'Gateway'
        db.delete_table('tinc_gateway_connect_to')

        # Deleting model 'Island'
        db.delete_table('tinc_island')

        # Deleting model 'TincAddress'
        db.delete_table('tinc_tincaddress')


    models = {
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

    complete_apps = ['tinc']