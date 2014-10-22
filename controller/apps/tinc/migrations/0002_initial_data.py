# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_tinc_server(apps, schema_editor):
    # Create server.tinc with name 'server' as tinc_name (backwards compatibility)
    ContentType = apps.get_model("contenttypes", "ContentType")
    ctype = ContentType.objects.get(app_label="nodes", model="server")
    
    server = apps.get_model("nodes", "Server").objects.first()
    
    TincHost = apps.get_model("tinc", "TincHost")
    tinc = TincHost.objects.create(content_type=ctype, object_id=server.pk, name='server')


def delete_tinc_server(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ctype = ContentType.objects.get(app_label="nodes", model="server")
    
    server = apps.get_model("nodes", "Server").objects.first()
    
    TincHost = apps.get_model("tinc", "TincHost")
    TincHost.objects.get(content_type=ctype, object_id=server.pk).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tinc', '0001_initial'),
        ('nodes', '0002_initial_data'),
    ]

    operations = [
        migrations.RunPython(create_tinc_server, delete_tinc_server)
    ]
