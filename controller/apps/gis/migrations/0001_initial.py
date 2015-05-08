# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_google_maps.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NodeGeolocation',
            fields=[
                ('address', django_google_maps.fields.AddressField(help_text=b'Enter the node location name (street, city, region...) The marker will be updated automatically.', max_length=200, null=True, blank=True)),
                ('geolocation', django_google_maps.fields.GeoLocationField(help_text=b'Geographic latitude and longitude. Updated automatically using the address. You can drag the marker in the map to make any correction if needed.', max_length=100, null=True, blank=True)),
                ('node', models.OneToOneField(related_name='gis', primary_key=True, serialize=False, to='nodes.Node')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
