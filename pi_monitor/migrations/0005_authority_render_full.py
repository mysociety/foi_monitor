# Generated by Django 3.0.4 on 2020-10-19 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pi_monitor', '0004_jurisdiction_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='authority',
            name='render_full',
            field=models.BooleanField(default=True),
        ),
    ]
