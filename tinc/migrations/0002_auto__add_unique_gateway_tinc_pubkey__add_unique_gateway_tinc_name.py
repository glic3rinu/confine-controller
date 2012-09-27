# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Gateway', fields ['tinc_pubkey']
        db.create_unique('tinc_gateway', ['tinc_pubkey'])

        # Adding unique constraint on 'Gateway', fields ['tinc_name']
        db.create_unique('tinc_gateway', ['tinc_name'])


    def backwards(self, orm):
        # Removing unique constraint on 'Gateway', fields ['tinc_name']
        db.delete_unique('tinc_gateway', ['tinc_name'])

        # Removing unique constraint on 'Gateway', fields ['tinc_pubkey']
        db.delete_unique('tinc_gateway', ['tinc_pubkey'])


    models = {
        'tinc.gateway': {
            'Meta': {'object_name': 'Gateway'},
            'connect_to': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tinc.TincAddress']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tinc_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'tinc_pubkey': ('django.db.models.fields.TextField', [], {'unique': 'True'})
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