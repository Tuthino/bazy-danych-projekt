from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_list_view, name='team_list'),
    path('create/', views.create_team_view, name='create_team'),
    path('<int:team_id>/manage/', views.manage_team_view, name='manage_team'),
]

