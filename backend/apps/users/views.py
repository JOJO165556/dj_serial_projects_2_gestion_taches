from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from services.user_service import create_user, update_user

def register_view(request):
    # Inscription
    if request.user.is_authenticated:
        return redirect("project_list")
        
    if request.method == "POST":
        create_user(
            username=request.POST.get("username"),
            email=request.POST.get("email"),
            password=request.POST.get("password")
        )
        return redirect("login")
    
    return render(request, "users/register.html")

def login_view(request):
    # Connexion
    if request.user.is_authenticated:
        return redirect("project_list")
        
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("project_list")
        
    return render(request, "users/login.html")

def logout_view(request):
    # Deconnexion
    logout(request)
    return redirect("login")

@login_required
def profile_view(request):
    # Affichage profil
    return render(request, "users/profile.html", {"user": request.user})

@login_required
def profile_edit(request):
    # Edition profil
    user = request.user
    if request.method == "POST":
        update_user(user, request.POST)
        return redirect("profile")
    return render(request, "users/profile_edit.html", {"user": user})