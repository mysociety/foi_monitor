# Generated by Django 3.0.4 on 2020-10-07 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pi_monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='special',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
