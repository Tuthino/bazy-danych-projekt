# This is for shared functions across all apps
from .models import User

def getSessionUser(request):
    user_id = request.session.get("user_id")  # Get user ID from session
    user = None

    if user_id:
        try:
            user = User.objects.get(id=user_id)  # Fetch user from the database

        except Username.DoesNotExist:
            pass
    return user

