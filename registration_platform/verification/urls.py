from django.urls import path
from .views import *

urlpatterns = [
    path('account/', UserAccountView.as_view(), name='account'),
]
