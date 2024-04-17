from django.urls import path
from .views import *

urlpatterns = [
    path('', GetAroundCenter.as_view()),
]
