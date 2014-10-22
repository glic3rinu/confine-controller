# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def init_testbed(apps, schema_editor):
    Testbed = apps.get_model("controller", "Testbed")
    testbed = Testbed.objects.create()
    
    TestbedParams = apps.get_model("controller", "TestbedParams")
    TestbedParams.objects.create(testbed=testbed)


def drop_testbed(apps, schema_editor):
    Testbed = apps.get_model("controller", "Testbed")
    Testbed.objects.all().delete()
    
    TestbedParams = apps.get_model("controller", "TestbedParams")
    TestbedParams.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_testbed, drop_testbed),
    ]
