# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-10-08 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researcher_UI', '0026_build_researcher_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
