from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import CreateView
from django.utils import timezone
# from django.template import loader
from django.db.models import Count
from django.contrib.auth.models import User


from .models import Account, Game, Character


class IndexView(generic.ListView):
    template_name = 'group_finder/index.html'
    context_object_name = 'latest_game_list'
    

    def get_queryset(self):
        """
        Return the last five created games.
        """

        return Game.objects.all().order_by('-creation_date')[:5].annotate(num_players=(Count('participants') - 1))
    

class DetailView(generic.DetailView):
    model = Game
    template_name = 'group_finder/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_participants = self.object.participants
        participant_names = []
        for participant in current_participants.all():
            participant_names.append(participant)
        context["participant_names"] = participant_names
        num_players = len(participant_names) - 1
        context["num_players"] = num_players
        context["last_participant"] = participant_names[num_players]

        return context

class AccountView(generic.ListView):
    template_name = 'group_finder/account.html'
    context_object_name = 'personal_game_list'


    def get_queryset(self):
        """
        Return your last five created/joined games.
        """
        # RIGHT NOW THIS JUST ASSUMES YOU ARE "ADMIN", MUST BE CHANGED WHEN LOGIN IS IMPLEMENTED
        
        return Account.objects.get(id=1).game_set.all().order_by('-creation_date')[:5]

        # ALSO COULD DISPLAY YOUR CHARACTER THAT YOU'RE PLAYING IN THIS GAME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_object = User.objects.get(id=1)
        
        context["username"] = user_object.username
        context["email"] = user_object.email
        context["first_name"] = user_object.first_name
        context["last_name"] = user_object.last_name
        context["date_joined"] = user_object.date_joined

        return context

def login(request):
    return render(request, 'group_finder/login.html')

def about(request):
    return render(request, 'group_finder/about.html')

class ManagementView(generic.ListView):
    template_name = 'group_finder/management.html'
    context_object_name = 'hosted_game_list'

    def get_queryset(self):
        """
        Return your last five created games.
        """
        # THIS MUST BE CHANGED TO GET ONLY CURRENT USER/ACCOUNT'S CREATED GAMES
        return Account.objects.get(id=1).game_set.all().filter(host_id=1).order_by('-creation_date')[:5]

class EditView(generic.DetailView):
    model = Game
    template_name = 'group_finder/edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_participants = self.object.participants
        participant_names = []
        for participant in current_participants.all():
            participant_names.append(participant)
        context["participant_names"] = participant_names
        num_players = len(participant_names) - 1
        context["num_players"] = num_players
        context["last_participant"] = participant_names[num_players]

        return context

def create(request):
    game_data = request.POST.get('gameName')
    campaign_data = request.POST.get('campaignName')
    game = Account.objects.get(id=1).game_set.create(game_text=game_data, campaign_text=campaign_data, host_id=1)
    game.save()
    # return redirect('detail', args=game.id)
    return redirect(f'/group_finder/{game.id}/')

class GameCreate(CreateView):
    model = Game
    fields = ['game_text', 'campaign_text']