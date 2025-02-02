from django.shortcuts import render, redirect, get_object_or_404
from functools import wraps
from users.shared import getSessionUser
from users.models import User 
from teams.models import Team, UserTeam

def user_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = getSessionUser(request)
        if not user:
            return redirect("login")  

        else:
            try:
                if not user.logged_in or not user.admin:
                    return redirect("permission_denied")  
            except User.DoesNotExist:
                return redirect("login")  

        
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def user_loggedin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = getSessionUser(request)
        if not user:
            return redirect("login") 
        
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def team_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = getSessionUser(request)
        if not user:
            return redirect("login") 

        # Extract the team_id from the URL arguments
        team_id = kwargs.get("team_id")
        if not team_id:
            return redirect("permission_denied")  

        # Check if the user is an admin of the team
        team = get_object_or_404(Team, id=team_id)
        is_team_admin = UserTeam.objects.filter(team=team, user=user, teamadmin=True).exists()

        if not is_team_admin:
            return redirect("permission_denied")  

       
        return view_func(request, *args, **kwargs)

    return _wrapped_view

