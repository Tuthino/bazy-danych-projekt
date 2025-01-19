from django.shortcuts import render, redirect, get_object_or_404
from .models import Team, UserTeam
from users.models import User  
from users.decorators import *
from users.shared import getSessionUser
from django.contrib import messages


@user_loggedin_required
def team_list_view(request):
    user = getSessionUser(request)
    teams = Team.objects.all()
    
    # Get all teams where the user is assigned in the UserTeam table
    user_teams = UserTeam.objects.filter(user=user.id).select_related("team")
        # Create a list to store team and admin status
    all_teams_status = []
    user_teams_status = [
    {"team": user_team.team, "is_admin": user_team.teamadmin}
    for user_team in user_teams
]
    for team in teams:
        teams = Team.objects.all()
        is_admin = UserTeam.objects.filter(team=team, user=user, teamadmin=True).exists()
        all_teams_status.append({"team": team, "is_admin": is_admin})

    return render(request, "teams/team_list.html", {"all_teams": all_teams_status,'user':user,'assigned_teams':user_teams_status})

@user_admin_required
def create_team_view(request):
    user = getSessionUser(request)

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            # Create the new team
            team = Team.objects.create(name=name)

            # Assign the user to the team and make them an admin
            UserTeam.objects.create(team=team, user=user, teamadmin=True)

            messages.success(request, f"Team '{team.name}' created successfully, and you have been assigned as admin!")
            return redirect("team_list")
        else:
            messages.error(request, "Team name is required.")
    return render(request, "teams/create_team.html",{'user':user})


@team_admin_required
def manage_team_view(request, team_id):
    # Fetch the team instance
    team = get_object_or_404(Team, id=team_id)

    # Fetch all users assigned to the team
    team_users = UserTeam.objects.filter(team=team)

    # Exclude users already assigned to the team from the available list
    assigned_user_ids = team_users.values_list('user_id', flat=True)
    users = User.objects.exclude(id__in=assigned_user_ids)

    if request.method == "POST":
        if "user_id" in request.POST:
            # Add a user to the team
            user_id = request.POST.get("user_id")
            if user_id:
                user = get_object_or_404(User, id=user_id)
                UserTeam.objects.create(team=team, user=user)
                messages.success(request, f"User {user.username} added to {team.name}.")
                return redirect("manage_team", team_id=team.id)
        elif "remove_user_id" in request.POST:
            # Remove a user from the team
            remove_user_id = request.POST.get("remove_user_id")
            user_to_remove = get_object_or_404(User, id=remove_user_id)
            UserTeam.objects.filter(team=team, user=user_to_remove).delete()
            messages.success(request, f"User {user_to_remove.username} removed from {team.name}.")
            return redirect("manage_team", team_id=team.id)

    # Get the currently logged-in user
    user = getSessionUser(request)

    return render(request, "teams/manage_team.html", {
        "team": team,
        "users": users,
        "team_users": team_users,  # Pass users in the team to the template
        "user": user,
    })
