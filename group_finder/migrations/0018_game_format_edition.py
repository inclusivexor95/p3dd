# Generated by Django 3.0.5 on 2020-04-17 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_finder', '0017_auto_20200416_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='format_edition',
            field=models.CharField(default='1', max_length=50, verbose_name='Format'),
            preserve_default=False,
        ),
    ]