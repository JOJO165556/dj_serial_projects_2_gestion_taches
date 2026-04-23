from django.urls import path
from .views import login_view, register_view, profile_edit, profile_view, logout_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("register/", register_view, name="register"),
]
