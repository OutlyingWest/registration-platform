from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import *

urlpatterns = [
    # Controllers for users management
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
