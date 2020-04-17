import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Game(models.Model):
    users = models.ManyToManyField(User)
    game_text = models.CharField(max_length=200, verbose_name=('Game Name'))
    campaign_text = models.CharField(max_length=200, verbose_name=('Campaign Name'))
    game_type = models.CharField(max_length=100, verbose_name=('Game'))
    format_edition = models.CharField(max_length=50, verbose_name=('Format'))
    creation_date = models.DateTimeField(('date created'), default=timezone.now)
    host_id = models.IntegerField()
    accepting_players = models.BooleanField(blank=False, default=True)
    applications = ArrayField(ArrayField(models.CharField(max_length=50), default=list), default=list, null=True)
    def __str__(self):
        return self.game_text
    def get_absolute_url(self):
        return reverse('group_finder:detail', kwargs={'pk': self.pk})



class Character(models.Model):
    name_text = models.CharField(max_length=50, verbose_name=('Character Name'))
    player_text = models.CharField(max_length=30, verbose_name=('Your Name'))
    race_text = models.CharField(max_length=30, verbose_name=('Character Race'))
    class_text = models.CharField(max_length=30, verbose_name=('Character Class'))
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    def __str__(self):
        return self.name_text
    def get_absolute_url(self):
        return reverse('group_finder:detail', kwargs={'pk': self.game.id})