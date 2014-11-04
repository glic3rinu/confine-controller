# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Initialize host name if is empty."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for host in orm.Host.objects.filter(name=''):
            host.name = 'Host %s' % host.pk
            host.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'nodes.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'tinc.host': {
            'Meta': {'object_name': 'Host'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Island']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tinc_hosts'", 'to': u"orm['users.User']"})
        },
        u'tinc.tincaddress': {
            'Meta': {'object_name': 'TincAddress'},
            'addr': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': u"orm['tinc.TincHost']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Island']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'port': ('django.db.models.fields.SmallIntegerField', [], {'default': "'655'"})
        },
        u'tinc.tinchost': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincHost'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'pubkey': ('controller.models.fields.RSAPublicKeyField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'users.group': {
            'Meta': {'ordering': "['name']", 'object_name': 'Group'},
            'allow_nodes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_slices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'users.roles': {
            'Meta': {'unique_together': "(('user', 'group'),)", 'object_name': 'Roles'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_group_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_node_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_slice_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['users.User']"})
        },
        u'users.user': {
            'Meta': {'ordering': "['name']", 'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'through': u"orm['users.Roles']", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('controller.models.fields.TrimmedCharField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('controller.models.fields.NullableCharField', [], {'db_index': 'True', 'max_length': '30', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tinc']
    symmetrical = True
