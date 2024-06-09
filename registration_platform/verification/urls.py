from django.urls import path
from .views import *

urlpatterns = [
    path('<int:user_id>/account/', UserAccountView.as_view(), name='account'),
    path('upload-document/', UserDocumentUploadView.as_view(), name='upload-document'),
]
