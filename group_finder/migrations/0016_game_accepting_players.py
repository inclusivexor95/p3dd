# Generated by Django 3.0.5 on 2020-04-17 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_finder', '0015_remove_game_accepting_players'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='accepting_players',
            field=models.BooleanField(blank=True, default=True),
            preserve_default=False,
        ),
    ]
