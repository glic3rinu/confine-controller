# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Testbed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestbedParams',
            fields=[
                ('testbed', models.OneToOneField(related_name=b'testbed_params', primary_key=True, serialize=False, to='controller.Testbed')),
                ('mgmt_ipv6_prefix', models.CharField(default=b'fd65:fc41:c50f::/48', help_text=b'An IPv6 /48 network used as the testbed management IPv6 prefix. See addressing for legal values. This member can only be changed if all nodes are in the safe set state (/set_state=safe).', max_length=128, validators=[django.core.validators.validate_ipv6_address])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
