# Generated by Django 3.0.5 on 2020-04-16 16:26

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_finder', '0013_game_applications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='applications',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), default=list, size=None), default=list, null=True, size=None),
        ),
    ]
