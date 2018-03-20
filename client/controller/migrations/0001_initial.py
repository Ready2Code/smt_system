# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-31 03:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ControllerSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('controller_name', models.CharField(max_length=30)),
                ('info_collector_ip', models.CharField(max_length=30)),
                ('info_collector_port', models.IntegerField()),
                ('info_websocket_ip', models.CharField(max_length=30)),
                ('info_websocket_port', models.IntegerField()),
            ],
        ),
    ]
