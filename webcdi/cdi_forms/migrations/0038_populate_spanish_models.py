# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-10 21:13
from __future__ import unicode_literals

from django.db import migrations, models
import os
import pandas as pd




def addSpanishData(apps, schema_editor):
    from django.conf import settings

    PROJECT_ROOT = settings.BASE_DIR
    spanish_wg_path = os.path.realpath(PROJECT_ROOT + '/cdi_form_csv/[Spanish_WG].csv')
    spanish_ws_path = os.path.realpath(PROJECT_ROOT + '/cdi_form_csv/[Spanish_WS].csv')

    Spanish_WG = apps.get_model('cdi_forms', 'Spanish_WG')
    Spanish_WS = apps.get_model('cdi_forms', 'Spanish_WS')

    spanish_wg_data=pd.read_csv(spanish_wg_path, sep=',')
    spanish_ws_data=pd.read_csv(spanish_ws_path, sep=',')

    Spanish_WG.objects.bulk_create([Spanish_WG(**vals) for vals in spanish_wg_data.to_dict('records')])
    Spanish_WS.objects.bulk_create([Spanish_WS(**vals) for vals in spanish_ws_data.to_dict('records')])


class Migration(migrations.Migration):

    dependencies = [
        ('cdi_forms', '0037_split_birthweight_into_us_and_si_units'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spanish_wg',
            name='definition',
            field=models.CharField(blank=True, max_length=1001, null=True),
        ),
        migrations.AlterField(
            model_name='spanish_wg',
            name='gloss',
            field=models.CharField(blank=True, max_length=1001, null=True),
        ),
        migrations.AlterField(
            model_name='spanish_ws',
            name='definition',
            field=models.CharField(blank=True, max_length=1001, null=True),
        ),
        migrations.AlterField(
            model_name='spanish_ws',
            name='gloss',
            field=models.CharField(blank=True, max_length=1001, null=True),
        ),
    	migrations.RunPython(addSpanishData)
    ]