from django.contrib import admin

from .models import Account, Game, Character
# Register your models here.


admin.site.register(Account)
admin.site.register(Game)
admin.site.register(Character)