from django.shortcuts import render
from users.models import User
from users.shared import getSessionUser

def dashboard_view(request):
    user = getSessionUser(request)

    return render(request, "dashboard/dashboard.html", {"user": user})
