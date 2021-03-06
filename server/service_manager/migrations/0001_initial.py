# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 08:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('programs', models.CharField(max_length=80)),
                ('signal_destip', models.CharField(max_length=30)),
                ('signal_port', models.IntegerField()),
                ('resource_broadcast_ip', models.CharField(max_length=30)),
                ('resource_broadband_ip', models.CharField(max_length=30)),
            ],
        ),
    ]
