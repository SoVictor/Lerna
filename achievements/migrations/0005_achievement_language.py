# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-26 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0004_auto_20171125_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='language',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]