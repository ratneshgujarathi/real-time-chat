from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("logoutUser", views.logoutUser, name="logoutUser"),
]
