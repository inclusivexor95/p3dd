
from django.urls import path

from . import views

app_name = 'group_finder'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('account/', views.AccountView.as_view(), name='account'),
    path('account/update/', views.edit_profile, name='account_update'),
    path('about/', views.about, name='about'),
    path('<int:pk>/join/', views.GameApply.as_view(), name='game_apply'),
    path('create/', views.GameCreate.as_view(), name='game_create'),
    path('<int:pk>/update/', views.GameUpdate.as_view(), name='game_update'),
    path('<int:pk>/delete/', views.GameDelete.as_view(), name='game_delete'),
    path('accounts/signup/', views.signup, name='signup'),
    path('<int:pk>/character/', views.CharCreate.as_view(), name='character_create'),
    path('<int:pk>/character/update', views.CharUpdate.as_view(), name='character_update'),
    path('<int:pk>/approve/<user_id_string>', views.Approve.as_view(), name='approve'),
    path('<int:pk>/deny/<user_id_string>', views.Deny.as_view(), name='deny'),
]