# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from IPy import IP

from controller.settings import MGMT_IPV6_PREFIX
from controller.utils.ip import int_to_hex_str
from controller.utils.system import run
from nodes.settings import NODES_NODE_API_BASE_URI_DEFAULT, NODES_SERVER_API_BASE_URI_DEFAULT

from nodes.models import ServerApi

# We need to copy here that because only model attributes stored
# in the database are accessible via south orm
def node_mgmt_address(node):
    ipv6_words = MGMT_IPV6_PREFIX.split(':')[:3]
    # MGMT_IPV6_PREFIX:N:0000::2/64
    ipv6_words.append(int_to_hex_str(node.id, 4))
    return IP(':'.join(ipv6_words) + '::2')

def server_mgmt_address(server):
    ipv6_words = MGMT_IPV6_PREFIX.split(':')[:3]
    # MGMT_IPV6_PREFIX:0:0000::2/128
    return IP(':'.join(ipv6_words) + '::2')


class Migration(DataMigration):

    def forwards(self, orm):
        """Create default NodeApi and ServerApi for existing objects."""
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

        # Create default NodeApi
        for node in orm.Node.objects.all():
            mgmt_addr = node_mgmt_address(node)
            url = NODES_NODE_API_BASE_URI_DEFAULT % {'mgmt_addr': mgmt_addr}
            orm.NodeApi.objects.create(node=node, base_uri=url, cert=node.cert)

        # Create two ServerApi for server (one for REGISTRY and another for CONTROLLER)
        if not orm.Server.objects.exists():
            # Create the main server
            description = run('hostname', display=False).stdout
            server = orm.Server.objects.create(description=description)
        
        for server in orm.Server.objects.all():
            mgmt_addr = server_mgmt_address(server)
            url = NODES_SERVER_API_BASE_URI_DEFAULT % {'mgmt_addr': mgmt_addr}
            orm.ServerApi.objects.create(server=server, base_uri=url, type=ServerApi.REGISTRY)
            orm.ServerApi.objects.create(server=server, base_uri=url, type=ServerApi.CONTROLLER)


    def backwards(self, orm):
        """Remove all the NodeApi and ServerApi objects."""
        # Try to restore node.cert
        for node in orm.Node.objects.all():
            if node.api and node.api.cert:
                node.cert = node.api.cert
                node.save()
        
        orm.NodeApi.objects.all().delete()
        orm.ServerApi.objects.all().delete()

    models = {
        u'nodes.directiface': {
            'Meta': {'unique_together': "(['name', 'node'],)", 'object_name': 'DirectIface'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'direct_ifaces'", 'to': u"orm['nodes.Node']"})
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
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Island']", 'null': 'True', 'blank': 'True'}),
            'local_iface': ('django.db.models.fields.CharField', [], {'default': "'eth0'", 'max_length': '16'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priv_ipv4_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '19', 'null': 'True', 'blank': 'True'}),
            'set_state': ('django.db.models.fields.CharField', [], {'default': "'debug'", 'max_length': '16'}),
            'sliver_mac_prefix': ('controller.models.fields.NullableCharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv4': ('django.db.models.fields.CharField', [], {'default': "'dhcp'", 'max_length': '8'}),
            'sliver_pub_ipv4_range': ('controller.models.fields.NullableCharField', [], {'default': "'#8'", 'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'sliver_pub_ipv6': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'})
        },
        u'nodes.nodeapi': {
            'Meta': {'object_name': 'NodeApi'},
            'base_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'cert': ('controller.models.fields.NullableTextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'api'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['nodes.Node']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'node'", 'max_length': '16'})
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
        u'nodes.serverapi': {
            'Meta': {'object_name': 'ServerApi'},
            'base_uri': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'cert': ('controller.models.fields.NullableTextField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'island': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nodes.Island']", 'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'api'", 'to': u"orm['nodes.Server']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'nodes.serverprop': {
            'Meta': {'unique_together': "(('server', 'name'),)", 'object_name': 'ServerProp'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'properties'", 'to': u"orm['nodes.Server']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
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

    complete_apps = ['nodes']
    symmetrical = True
