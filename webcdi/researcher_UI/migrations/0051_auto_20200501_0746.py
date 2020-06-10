# Generated by Django 2.2.6 on 2020-05-01 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researcher_UI', '0050_merge_20200421_0637'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='redirect_boolean',
            field=models.BooleanField(default=False, verbose_name='Provide redirect button at completion of study?'),
        ),
        migrations.AddField(
            model_name='study',
            name='redirect_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
