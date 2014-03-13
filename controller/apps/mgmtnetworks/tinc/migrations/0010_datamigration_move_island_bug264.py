# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("nodes", "0006_auto__add_field_node_island"),
    )

    def forwards(self, orm):
        """ Copy TincClient island to Node and Host. """
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for tclient in orm.TincClient.objects.filter(island__isnull=False):
            ct = ContentType.objects.get_for_id(tclient.content_type.id)
            try:
                content_object = ct.get_object_for_this_type(id=tclient.object_id)
            except ObjectDoesNotExist:
                # FIXME: cleanup orphan objects pointed by tclient?
                #print tclient.pk, ct, tclient.object_id
                continue
            content_object.island_id = tclient.island_id
            content_object.save()


    def backwards(self, orm):
        """ Copy Node and Host island to TincClient. """
        for tclient in orm.TincClient.objects.all():
            ct = ContentType.objects.get_for_id(tclient.content_type.id)
            try:
                content_object = ct.get_object_for_this_type(id=tclient.object_id)
            except ObjectDoesNotExist:
                # FIXME: cleanup orphan objects pointed by tclient?
                #print tclient.pk, ct, tclient.object_id
                continue
            tclient.island_id = content_object.island_id
            tclient.save()


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'nodes.directiface': {
            'Meta': {'unique_together': "(['name', 'node'],)", 'object_name': 'DirectIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'direct_ifaces'", 'to': u"orm['nodes.Node']"})
        },
        u'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'arch': ('django.db.models.fields.CharField', [], {'default': "'i686'", 'max_length': '16'}),
            'boot_sn': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'cert': ('controller.models.fields.NullableTextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': u"orm['users.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']", 'null': 'True', 'blank': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priv_ipv4_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '19', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'debug'", 'max_length': '16'}),
            'sliver_mac_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4': ('django.db.models.fields.CharField', [], {'default': "'dhcp'", 'max_length': '8'}),
            'sliver_pub_ipv4_range': ('controller.models.fields.NullableCharField', [], {'default': "'#8'", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv6': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'})
        },
        u'nodes.nodeprop': {
            'Meta': {'unique_together': "(('node', 'name'),)", 'object_name': 'NodeProp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': u"orm['nodes.Node']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'nodes.server': {
            'Meta': {'object_name': 'Server'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tinc.gateway': {
            'Meta': {'object_name': 'Gateway'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tinc.host': {
            'Meta': {'object_name': 'Host'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']", 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tinc_hosts'", 'to': u"orm['users.User']"})
        },
        u'tinc.island': {
            'Meta': {'object_name': 'Island'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'tinc.tincaddress': {
            'Meta': {'object_name': 'TincAddress'},
            'addr': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']", 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.SmallIntegerField', [], {'default': "'655'"}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': u"orm['tinc.TincServer']"})
        },
        u'tinc.tincclient': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincClient'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tinc.Island']", 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'pubkey': ('controller.models.fields.RSAPublicKeyField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'tinc.tincserver': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'TincServer'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_researcher': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_technician': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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

    complete_apps = ['nodes', 'tinc']
    symmetrical = True
