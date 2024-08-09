from django.urls import path
from .views import *

urlpatterns = [
    path('', ImageView.as_view()),
    path('/all', ImageBulkUploadView.as_view()),
    path('/generate', GenerateImageView.as_view()),
]
