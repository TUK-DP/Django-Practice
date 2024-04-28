from django.urls import path
from .views import *

urlpatterns = [
    path('', GetQuizView.as_view()),
]
