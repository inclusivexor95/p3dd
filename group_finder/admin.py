from django.contrib import admin

from .models import Game, Character, Account
# Register your models here.


# admin.site.register(Account)
admin.site.register(Game)
admin.site.register(Character)
admin.site.register(Account)