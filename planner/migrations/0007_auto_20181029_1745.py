# Generated by Django 2.0.3 on 2018-10-30 00:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0006_auto_20181027_1244'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='county',
        ),
        migrations.RemoveField(
            model_name='route',
            name='jurisdiction',
        ),
    ]
