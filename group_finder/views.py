from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
# from django.template import loader
from django.db.models import Count
from django.urls import reverse_lazy, reverse

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Game, Character
from .forms import CreateGameForm,UpdateGameForm

# import django.dispatch
# apply_signal = django.dispatch.Signal(providing_args=['game_id', 'user_object'])



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

#need to add host name in detail page
        
        # characters = self.object.character_set.all()
        context["characters"] = self.object.character_set.all()
        return context
    
    

class AccountView(LoginRequiredMixin, generic.ListView):
    template_name = 'group_finder/account.html'
    context_object_name = 'personal_game_list'

    def get_queryset(self):

        user_game = Game.objects.filter(users__pk=self.request.user.id)

        user_game.order_by('-creation_date')

        for game in user_game:
            game.host = str(User.objects.get(id = game.host_id))
            if self.request.user.id == game.host_id:
                game.host += ' (You)'


        for game in user_game:
            if game.host_id == self.request.user.id:
                if len(game.applications) > 0:
                    game.application_username = []
                    for application in game.applications:
                        game.application_username.append(f'{application[0]} userid:{application[1]}')

        

        return user_game

        # ALSO COULD DISPLAY YOUR CHARACTER THAT YOU'RE PLAYING IN THIS GAME

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_object = self.request.user
        
        context["username"] = user_object.username
        context["email"] = user_object.email
        context["first_name"] = user_object.first_name
        # context["last_name"] = user_object.last_name
        context["date_joined"] = user_object.date_joined
        
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
        hosted_games = Game.objects.filter(users=self.request.user).filter(host_id=self.request.user.id).order_by('-creation_date')

        for game in hosted_games:
            if len(game.applications) > 0:
                game.application_username = []
                for application in game.applications:
                    game.application_username.append(application[0])

        # CURRENT USER/ACCOUNT'S CREATED GAMES
        return hosted_games

# class EditView(LoginRequiredMixin,generic.DetailView):
#     model = Game
#     template_name = 'group_finder/edit.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         current_participants = self.object.users
#         participant_names = []
#         for participant in current_participants.all():
#             participant_names.append(participant)
#         context["participant_names"] = participant_names
#         num_players = len(participant_names) - 1
#         context["num_players"] = num_players
#         context["last_participant"] = participant_names[num_players]

#         return context

class GameCreate(LoginRequiredMixin, CreateView):
    form_class = CreateGameForm
    model = Game
    # fields = ['game_text', 'campaign_text','game_type']
    
    def form_valid(self,form):
        form.instance.host_id = self.request.user.id
        self.object = form.save()
        self.object.users.add(User.objects.get(id=self.request.user.id))
        messages.success(self.request,"The game post was created successfully!")
        return super().form_valid(form)

class GameUpdate(LoginRequiredMixin, SuccessMessageMixin,UpdateView):
    success_message = "The game post was updated!"
    form_class = UpdateGameForm
    model = Game

class CharCreate(LoginRequiredMixin, CreateView):
    # form_class = CreateCharForm
    model = Character
    fields = ['name_text', 'player_text', 'race_text', 'class_text']

    def form_valid(self, form):
        form.instance.game = Game.objects.get(id=self.kwargs['pk'])
        messages.success(self.request,"The character was created successfully!")
        return super().form_valid(form)


class GameDelete(LoginRequiredMixin, DeleteView):
    model = Game
    success_url = '/group_finder/account'
    success_message = "The game post was deleted!"
    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(GameDelete, self).delete(request, *args, **kwargs)

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

#need to build in a more dynamic error message
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

class GameApply(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        current_game_id = self.kwargs['pk']
        # apply_signal.send(sender=self.__class__, game_id=current_game_id, user_object=self.request.user)

        current_game = Game.objects.get(id = current_game_id)

        user_id_string = str(self.request.user.id)

        user_name_string = str(self.request.user)

        if [user_name_string, user_id_string] not in current_game.applications:
            current_game.applications.append([user_name_string, user_id_string])
            current_game.save()

        return redirect(reverse('group_finder:detail', kwargs={'pk': current_game_id}))

class Approve(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        current_game_id = self.kwargs['pk']
        raw_user_id_string = self.kwargs['user_id_string']
        user_id_array = raw_user_id_string.split('userid:')
        user_id_string = user_id_array[1]
        current_game = Game.objects.get(id = current_game_id)

        current_user_id = int(user_id_string)
        current_user = User.objects.get(id=current_user_id)
        user_name_string = str(current_user)

        current_game.users.add(current_user)
        current_game.applications.remove([user_name_string, user_id_string])

        current_game.save()

        return redirect(reverse('group_finder:account'))
        



class Deny(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        current_game_id = self.kwargs['pk']
        raw_user_id_string = self.kwargs['user_id_string']
        user_id_array = raw_user_id_string.split('userid:')
        user_id_string = user_id_array[1]
        current_game = Game.objects.get(id = current_game_id)

        
        current_user_id = int(user_id_string)
        current_user = User.objects.get(id=current_user_id)
        user_name_string = str(current_user)

        current_game.applications.remove([user_name_string, user_id_string])

        current_game.save()

        return redirect(reverse('group_finder:account'))

