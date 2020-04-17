from django import forms
from .models import Game, Character
from django.contrib.auth.models import User


GAME_TYPE_CHOICES = [
    ('', ''),
    ('Dungeons and Dragons', 'D&D'), 
    ('Magic the Gathering', 'Magic the Gathering'),
    ('Board Games', 'Board Games'),
    ('Yu-Gi-Oh TCG', 'Yu-Gi-Oh TCG'),
    ('Pokemon TCG', 'Pokemon TCG'),
    ('Pathfinder', 'Pathfinder'),
    ('Warhammer', 'Warhammer'),
    ('Other', 'Other')
]

class CreateGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            'game_text',
            'campaign_text',
            'game_type'
        ]
        widgets = {
            'game_type': forms.Select(choices=GAME_TYPE_CHOICES)
        }

class UpdateGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            'game_text',
            'campaign_text',
            'game_type',
            'accepting_players'
        ]
        widgets = {
            'game_type': forms.Select(choices=GAME_TYPE_CHOICES)
        }


class ChangeUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'email'
        ]
        
    def __init__(self, *args, **kwargs):
        super(ChangeUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Display Name'
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_object = self.request.user
        context["first_name"] = user_object.first_name        
        return context
    def clean_password(self):
        return self.initial["password"]
