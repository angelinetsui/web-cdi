# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-29 14:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cdi_forms', '0050_auto_20190328_1634'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choices',
            old_name='choice_set_fr',
            new_name='choice_set_fr_ca',
        ),
    ]