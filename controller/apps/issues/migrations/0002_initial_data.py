# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def init_queues(apps, schema_editor):
    Queue = apps.get_model("issues", "Queue")
    Queue.objects.bulk_create([
        Queue(name="Web Interface", default=True),
        Queue(name="Nodes", notify_node_admins=True),
        Queue(name="Support"),
        Queue(name="Legal"),
        Queue(name="Administration"),
        Queue(name="Community Networks"),
        Queue(name="Other"),
        Queue(name="Documentation"),
    ])

def drop_queues(apps, schema_editor):
    Queue = apps.get_model("issues", "Queue")
    Queue.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_queues, drop_queues),
    ]
