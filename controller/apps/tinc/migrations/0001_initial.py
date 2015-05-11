# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import controller.apps.tinc.models
import controller.core.validators
import django.db.models.deletion
from django.conf import settings
import controller.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The unique name for this host. A single non-empty line of free-form text with no whitespace surrounding it.', unique=True, max_length=256, validators=[controller.core.validators.validate_name])),
                ('description', models.TextField(help_text=b'An optional free-form textual description of this host.', blank=True)),
                ('island', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='nodes.Island', help_text=b'An optional island used to hint where this tinc client reaches to.', null=True)),
                ('owner', models.ForeignKey(related_name='tinc_hosts', to=settings.AUTH_USER_MODEL, help_text=b'The user who administrates this host (its creator by default)')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TincAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('addr', models.CharField(help_text=b'The tinc IP address or host name of the host this one connects to.', max_length=128, verbose_name=b'address', validators=[controller.core.validators.validate_tinc_address])),
                ('port', models.SmallIntegerField(default=b'655', help_text=b'TCP/UDP port of this tinc address.')),
            ],
            options={
                'verbose_name_plural': 'tinc addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TincHost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name given to this host in the tinc network, usually TYPE_ID (e.g. server_4).', unique=True, max_length=32)),
                ('pubkey', controller.models.fields.RSAPublicKeyField(help_text=b'PEM-encoded RSA public key used on tinc management network.', unique=True, null=True, verbose_name=b'public Key', blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('default_connect_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='tinc.TincHost', null=True)),
            ],
            options={
                'ordering': ['content_type', 'object_id'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tinchost',
            unique_together=set([('content_type', 'object_id')]),
        ),
        migrations.AddField(
            model_name='tincaddress',
            name='host',
            field=models.ForeignKey(related_name='addresses', to='tinc.TincHost'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tincaddress',
            name='island',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='nodes.Island', help_text=b'<a href="http://wiki.confine-project.eu/arch:rest-api#island_at_registry">Island</a> this tinc address is reachable from.', null=True),
            preserve_default=True,
        ),
    ]
