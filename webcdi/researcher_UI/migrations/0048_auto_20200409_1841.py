# Generated by Django 2.2.6 on 2020-04-09 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researcher_UI', '0047_auto_20200409_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measure',
            name='value',
            field=models.IntegerField(default=1),
        ),
    ]