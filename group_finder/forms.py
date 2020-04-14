from django import forms
from .models import Game


GAME_TYPE_CHOICES = [
    ('', ''),
    ('dnd', 'D&D'), 
    ('magic', 'Magic the Gathering'),
    ('boardGame', 'Board Games'),
    ('yugioh', 'Yu-Gi-Oh TCG'),
    ('pokemon', 'Pokemon TCG'),
    ('pathfinder', 'Pathfinder'),
    ('warhammer', 'Warhammer'),
    ('other', 'Other')
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