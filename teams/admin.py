from django.contrib import admin
from .models import Team, UserTeam

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'equipment_admin']

@admin.register(UserTeam)
class UserTeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'team', 'user','teamadmin']

