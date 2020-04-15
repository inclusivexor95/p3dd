from django import forms
from .models import Game, Character


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
