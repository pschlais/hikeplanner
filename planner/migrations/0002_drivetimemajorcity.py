# Generated by Django 2.0.3 on 2018-09-08 23:35

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriveTimeMajorCity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drive_distance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('drive_time', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('date_updated', models.DateField(default=datetime.date(1900, 1, 1))),
                ('api_call_status', models.IntegerField(choices=[(1, 'New Item'), (2, 'OK'), (3, 'Error')], default=1)),
                ('majorcity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.MajorCity')),
                ('trailhead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.Trailhead')),
            ],
        ),
    ]