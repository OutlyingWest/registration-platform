from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import *


urlpatterns = [
    path('', MainView.as_view(), name='index'),
]
