# Generated by Django 3.0.5 on 2020-04-17 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_finder', '0019_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='notification',
            field=models.CharField(default='None', max_length=200),
        ),
    ]
