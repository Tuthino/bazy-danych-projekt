
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list_view, name='ticket_list'),
    path('create/', views.ticket_create_view, name='ticket_create'),
    path('<int:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
    path('my_teams_tickets/', views.my_team_tickets_view, name='my_teams_tickets'),
]
