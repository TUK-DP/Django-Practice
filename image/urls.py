from django.urls import path
from .views import *

urlpatterns = [
    path('', ImageView.as_view()),
    path('/generate', GenerateImageView.as_view()),
    path('/test', TestView.as_view()),
    path('/test2', TestView2.as_view()),
    path('/test3', TestView3.as_view()),
]
