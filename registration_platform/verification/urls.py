from django.urls import path
from .views import *

urlpatterns = [
    path('account/', UserAccountView.as_view(), name='account'),
    path('upload-document/', UserDocumentUploadView.as_view(), name='upload-document'),
]
