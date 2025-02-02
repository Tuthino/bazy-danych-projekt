# Create your views here.
from .models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .shared import getSessionUser

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        # Validate inputs
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "register.html")

        # Hash the password
        hashed_password = make_password(password)

        # Create the user using Django ORM
        try:
            user = User.objects.create(
                username=username,
                password=hashed_password,
                email=email,
                logged_in=False,
                admin=False,
            )
            messages.success(request, "Registration successful.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Registration failed: {e}")
    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Validate inputs
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "login.html")

        try:
            user = User.objects.get(username=username)

            if check_password(password, user.password):
                # Mark the user as logged in (example, set session)
                request.session["user_id"] = user.id
                user.logged_in = True
                user.save()
                messages.success(request, "Login successful.")
                return redirect("dashboard")  
            else:
                messages.error(request, "Invalid username or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

def logout_view(request):
    #We are using Django's logout() func, which deletes session, additionally we  unset logged_in variable
    """Logs out the user and marks them as logged out in the database."""
    user = getSessionUser(request)
    if user:
        try:
            user.logged_in = False  # Mark the user as logged out
            user.save()
        except User.DoesNotExist:
            pass  # If the user doesn't exist, just proceed with logout

    # Perform the actual logout (clears session)
    logout(request)

    messages.success(request, "Logged out successfully.")
    return redirect("login")

def permission_denied_view(request):
    return render(request, "permission_denied.html", status=403)
