from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
# from django.template import loader
from django.db.models import Count
from django.urls import reverse_lazy, reverse

from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Game, Character
from .forms import CreateGameForm


class IndexView(generic.ListView):
    template_name = 'group_finder/index.html'
    context_object_name = 'latest_game_list'
    def get_queryset(self):

        if self.request.GET:

            form = self.request.GET

            games = Game.objects.all().annotate(num_players=(Count('users')))

            if form.get('searchGame', ''):
                games = games.filter(game_text__icontains=(form.get('searchGame', '')))
            if form.get('searchCampaign', ''):
                games = games.filter(campaign_text__icontains=(form.get('searchCampaign', '')))

            # do this later
            # if form.newPlayers == True:
            # elif form.newPlayers == False:
            # if form.get('newPlayers', ''):
            #     games = games.filter(accepting_players__contains)

            sort = form.get('sortBy', 'recent')
            
            if sort == 'recent':
                games = games.order_by('-creation_date')
            elif sort == 'name':
                games = games.order_by('game_text')
            elif sort == 'numPlayersAscending':
                games = games.order_by('num_players')
            elif sort == 'numPlayersDescending':
                games = games.order_by('-num_players')
        

        else:

            games = Game.objects.all().annotate(num_players=(Count('users'))).order_by('-creation_date')

        return games

class DetailView(generic.DetailView):
    model = Game
    template_name = 'group_finder/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_participants = self.object.users
        participant_names = []
        for participant in current_participants.all():
            participant_names.append(participant)
        context["participant_names"] = participant_names
        num_players = len(participant_names)
        context["num_players"] = num_players
        if num_players >= 1:
            context["last_participant"] = participant_names[num_players - 1]
        elif num_players == 1:
            context["last_participant"] = participant_names[0]
        
        # characters = self.object.character_set.all()
        context["characters"] = self.object.character_set.all()

        return context


class AccountView(LoginRequiredMixin, generic.ListView):
    template_name = 'group_finder/account.html'
    context_object_name = 'personal_game_list'

    def get_queryset(self):

        user_game = Game.objects.filter(users__pk=self.request.user.id)
        
        return user_game.order_by('-creation_date')

        # ALSO COULD DISPLAY YOUR CHARACTER THAT YOU'RE PLAYING IN THIS GAME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_object = self.request.user
        
        context["username"] = user_object.username
        context["email"] = user_object.email
        context["first_name"] = user_object.first_name
        # context["last_name"] = user_object.last_name
        context["date_joined"] = user_object.date_joined

        user_game = Game.objects.filter(users__pk=self.request.user.id)
        user_game.order_by('-creation_date')

        # hosts = {}
        # for game in user_game:
        #     hosts[f"{game.id}"] = [(User.objects.get(id = game.host_id)), (game.game_text)]

        # context["hosts"] = hosts.items() 
        
        return context


def about(request):
    return render(request, 'group_finder/about.html')

class ManagementView(LoginRequiredMixin, generic.ListView):
    template_name = 'group_finder/management.html'
    context_object_name = 'hosted_game_list'

    def get_queryset(self):
        """
        Return your created games.
        """
        # CURRENT USER/ACCOUNT'S CREATED GAMES
        # yvonne: deleted [:5] cause we want to see all of the user created games i think
        return Game.objects.filter(users=self.request.user).filter(host_id=1).order_by('-creation_date')

class EditView(LoginRequiredMixin,generic.DetailView):
    model = Game
    template_name = 'group_finder/edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_participants = self.object.users
        participant_names = []
        for participant in current_participants.all():
            participant_names.append(participant)
        context["participant_names"] = participant_names
        num_players = len(participant_names) - 1
        context["num_players"] = num_players
        context["last_participant"] = participant_names[num_players]

        return context


class GameCreate(LoginRequiredMixin, CreateView):
    form_class = CreateGameForm
    model = Game

    def form_valid(self, form):
        form.instance.host_id = self.request.user.id
        self.object = form.save()
        self.object.users.add(User.objects.get(id=self.request.user.id))
        return super().form_valid(form)


class CharCreate(LoginRequiredMixin, CreateView):
    # form_class = CreateCharForm
    model = Character
    fields = ['name_text', 'player_text', 'race_text', 'class_text']

    def form_valid(self, form):
        form.instance.game = Game.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=32,label = "Display Name", required=True)
    email = forms.EmailField(label = "Email", required=True)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')
    
    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.display_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user 


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/group_finder/')
        else:
            error_message = "Invalid sign up - please try again"
    form = SignUpForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)