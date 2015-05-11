# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from IPy import IP

from controller.apps.nodes.settings import NODES_SERVER_API_BASE_URI_DEFAULT
from controller.settings import MGMT_IPV6_PREFIX
from controller.utils.system import run
from controller.utils.ip import int_to_hex_str, split_len


def server_mgmt_address(server):
    # MGMT_IPV6_PREFIX:0:0000:rrrr:rrrr:rrrr/128
    ipv6_words = MGMT_IPV6_PREFIX.split(':')[:3]
    ipv6_words.extend(['0', '0000'])
    ipv6_words.extend(split_len(int_to_hex_str(server.id, 12), 4))
    return IP(':'.join(ipv6_words))


def create_main_server(apps, schema_editor):
    Server = apps.get_model("nodes", "Server")
    
    if Server.objects.exists():
        return # data already created
    
    server = Server.objects.create(name=run('hostname', display=False).stdout)
    
    # server.pk should be 2 (#245 backwards compatibility)
    # but we don't set directly PK to avoid problems with DB autoincrement
    if server.pk == 1:
        server.delete()
        server = Server.objects.create(name=server.name)
    elif server.pk > 2:
        server.delete()
        server.pk = 2
        server.save()
    assert server.pk == 2, "Server PK should be 2: %i" % server.pk
    
    # Initialize default Server API
    ServerApi = apps.get_model("nodes", "ServerApi")
    mgmt_addr = server_mgmt_address(server)
    url = NODES_SERVER_API_BASE_URI_DEFAULT % {'mgmt_addr': mgmt_addr}
    ServerApi.objects.create(server=server, base_uri=url, type='registry')
    ServerApi.objects.create(server=server, base_uri=url, type='controller')
    
    # TODO: create mgmt_net, tinc and other related objects???


def delete_main_server(apps, schema_editor):
    Server = apps.get_model("nodes", "Server")
    Server.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_main_server, delete_main_server),
    ]
