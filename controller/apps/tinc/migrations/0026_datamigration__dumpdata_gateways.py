# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

import json
import logging

from controller.utils import get_project_root
from django.core import serializers
from os import path

class Migration(DataMigration):
    GATEWAYS_FILE = path.join(get_project_root(), 'gateways.json')

    def forwards(self, orm):
        """
        Dump the gateways in the database (if any) to a file
        and warn the user that should migrate manually them.
        """
        if orm.Gateway.objects.exists():
            qs_gw = orm.Gateway.objects.all()

            # keep related objects: mgmtnetconf + tinc + addresses
            gw_ids = qs_gw.values_list('pk', flat=True)
            ctype = orm['contenttypes.ContentType'].objects.get(app_label='tinc', model='gateway')

            qs_mgmtnet = orm['mgmtnetworks.MgmtNetConf'].objects.filter(content_type=ctype, object_id__in=gw_ids)
            qs_thost = orm.TincHost.objects.filter(content_type=ctype, object_id__in=gw_ids)
            qs_taddr = orm.TincAddress.objects.filter(host_id__in=qs_thost.values_list('pk', flat=True))

            all_objects = list(qs_gw) + list(qs_mgmtnet) + list(qs_thost) + list(qs_taddr)

            # dump data to a file
            with open(self.GATEWAYS_FILE, "w") as out:
                serializers.serialize("json", all_objects, indent=4, stream=out)

            # remove all data to avoid orphan objects
            qs_taddr.delete()
            qs_thost.delete()
            qs_mgmtnet.delete()
            qs_gw.delete()

            # warn user
            logging.warning("As discussed on issue #236, gateways disappear "
                "from testbed architecture. Sorry but automatic migration is not "
                "possible. As some gateways exists in your testbed, manually "
                "intervention is required to create equivalent servers.\n"
                "NOTE: Gateway data has been dumped as json in %s" % self.GATEWAYS_FILE)

    def backwards(self, orm):
        """
        Code to restore gateways from the dumped file.

        As Gateway models doesn't exists anymore, this code
        will be 'best-efforts' executed during the migration
        and is only provided to help operators.

        If for any reason doesn't works properly, follow
        the next steps to restore manually the gateways:
        1. Restore tinc/models.py to include Gateway model.
        2. Load data using django-admin.py loaddata
        """
        try:
            data = open(self.GATEWAYS_FILE, "r").read()
        except IOError:
            logging.warning("Gateways NOT restored: cannot open file '%s'" % self.GATEWAYS_FILE)
            return # Doesn't exist gateway backup
        try:
            datajs = json.loads(data)
        except ValueError:
            logging.warning("Gateways NOT restored: invalid JSON format (loaded file '%s')" % self.GATEWAYS_FILE)
            return # Invalid JSON format

        # handle gateways and create via south ORM
        for key, obj in enumerate(datajs):
            if obj['model'] == 'tinc.gateway':
                gateway = datajs.pop(key)
                orm.Gateway.objects.create(pk=obj['pk'], **gateway['fields'])

        # Update Gateway auto id sequence
        db.execute("SELECT setval('tinc_gateway_id_seq', (SELECT MAX(id) FROM tinc_gateway))")

        # handle related objects
        data = json.dumps(datajs)
        for obj in serializers.deserialize("json", data):
            obj.save()


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'mgmtnetworks.mgmtnetconf': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'MgmtNetConf'},
            'backend': ('django.db.models.fields.CharField', [], {'default': "'tinc'", 'max_length': '16'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'nodes.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'tinc.gateway': {
            'Meta': {'object_name': 'Gateway'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tinc.host': {
            'Meta': {'object_name': 'Host'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
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

    complete_apps = ['mgmtnetworks', 'tinc']
    symmetrical = True
