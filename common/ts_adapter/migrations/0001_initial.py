# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-28 08:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TsAdapterSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src_addr', models.CharField(max_length=30)),
                ('dest_addr', models.CharField(max_length=30)),
            ],
        ),
    ]
