from django.urls import path

from . import views

app_name = 'group_finder'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('login/', views.login, name='login'),
    path('account/', views.AccountView.as_view(), name='account'),
    path('about/', views.about, name='about'),
    path('management/', views.ManagementView.as_view(), name='management'),
    path('edit/', views.ManagementView.as_view(), name='edit')
]