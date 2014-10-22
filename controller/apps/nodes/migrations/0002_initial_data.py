# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from controller.utils.system import run


def create_main_server(apps, schema_editor):
    Server = apps.get_model("nodes", "Server")
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
