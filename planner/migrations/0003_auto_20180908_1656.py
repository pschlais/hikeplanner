# Generated by Django 2.0.3 on 2018-09-08 23:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_drivetimemajorcity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drivetimemajorcity',
            name='drive_distance',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='drivetimemajorcity',
            name='drive_time',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]