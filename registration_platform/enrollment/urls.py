from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import *


urlpatterns = [
    path('', main_view, name='index'),
]
