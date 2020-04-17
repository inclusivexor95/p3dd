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

from .models import Game, Character, Account
from .forms import CreateGameForm,UpdateGameForm,ChangeUserForm

from django.core.mail import send_mail

# import django.dispatch
# from django.core.signals import request_finished
# from django.dispatch import receiver
# apply_signal = django.dispatch.Signal(providing_args=['game_id', 'user_object'])

# from django.template import Context, Template



def app_redirect(self):
    return redirect(reverse('group_finder:index'))

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
            if user.email and User.objects.filter(email=user.email).exclude(username=user.username).exists():
                context = {'form': form, 'error_message': 'This email address has already been used'}
                user.delete()
                return render(request, 'registration/signup.html', context)
            login(request, user)
            return redirect('/group_finder/')
        else:
            error_message = "Invalid Signup: either your username has been taken or your passwords did not fulfill the requirement"
    form = SignUpForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

def about(request):
    return render(request, 'group_finder/about.html')

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
            
            if form.get('newPlayers') == 'on':
                games = games.filter(accepting_players=True)

            if form.get('chooseGame', ''):
                games = games.filter(game_type=(form.get('chooseGame')))

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

    def get_context_data(self, **kwargs):

        if not self.request.GET:
            context = super().get_context_data(**kwargs)
            if self.request.user.id: 
                if self.request.user.account:
                    if self.request.user.account.notification != 'None':
                        context["notification"] = self.request.user.account.notification

        return context

class DetailView(generic.DetailView):
    model = Game
    template_name = 'group_finder/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_participants = self.object.users
        participant_names = []
        in_game = False
        for participant in current_participants.all():
            if participant.id == self.request.user.id:
                participant_names.append(str(participant) + '(You)')
                in_game = True
            else:
                participant_names.append(str(participant))
        
        context["in_game"] = in_game

        host_object = User.objects.get(id=self.object.host_id)
        if host_object.id == self.request.user.id:
            context["host"] = str(host_object) + '(You)'
        else:
            context["host"] = str(host_object)

        if self.object.game_type == 'Dungeons and Dragons' or self.object.game_type == 'Pathfinder':
            context["character"] = True
        else:
            context["character"] = False

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


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ChangeUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('group_finder:account'))
    else:
        form = ChangeUserForm(instance=request.user)
        
        args = {'form':form}
        return render(request, 'group_finder/account_form.html', args)


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

class GameCreate(LoginRequiredMixin, CreateView):
    form_class = CreateGameForm
    model = Game
    
    def form_valid(self,form):
        form.instance.host_id = self.request.user.id
        self.object = form.save()
        self.object.users.add(User.objects.get(id=self.request.user.id))
        messages.success(self.request,"The game post is created successfully!")
        return super().form_valid(form)

class GameUpdate(LoginRequiredMixin, SuccessMessageMixin,UpdateView):
    success_message = "The game post is updated!"
    form_class = UpdateGameForm
    model = Game

class CharCreate(LoginRequiredMixin, CreateView):
    # form_class = CreateCharForm
    model = Character
    fields = ['name_text', 'player_text', 'race_text', 'class_text']

    def form_valid(self, form):
        form.instance.game = Game.objects.get(id=self.kwargs['pk'])
        messages.success(self.request,"The character is created successfully!")
        return super().form_valid(form)


class GameDelete(LoginRequiredMixin, DeleteView):
    model = Game
    success_url = '/group_finder/account'
    success_message = "Deleted"
    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super(GameDelete, self).delete(request, *args, **kwargs)


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

            host = Account.objects.get(id=current_game.host_id)

            host.notification = current_game.game_text
            host.save()

            # apply_signal.send(sender=self.__class__, game_id=current_game_id, user_object=self.request.user)
        

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


        return reverse('group_finder:detail', kwargs={'pk': current_game_id})



# def send_email(request):
#     subject = request.POST.get('subject', '')
#     message = request.POST.get('message', '')
#     from_email = request.POST.get('from_email', '')
#     if subject and message and from_email:
#         try:
#             send_mail(subject, message, from_email, ['admin@example.com'])
#         except BadHeaderError:
#             return HttpResponse('Invalid header found.')
#         return HttpResponseRedirect('/contact/thanks/')
#     else:
#         # In reality we'd use a form class
#         # to get proper validation errors.
#         return HttpResponse('Make sure all fields are entered and valid.')


# @receiver(apply_signal)
# def apply_popup(sender, **kwargs):
    