from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

# Auth routes (SPEC §6). Login/logout use Django's built-in views.
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
