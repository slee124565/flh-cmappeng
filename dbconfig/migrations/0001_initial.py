# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-20 12:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(max_length=20, verbose_name='App Name Index Key')),
                ('json_data', models.TextField(default='', verbose_name='App Option Json Data')),
            ],
        ),
    ]
