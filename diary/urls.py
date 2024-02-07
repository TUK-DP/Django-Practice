from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiaryView

urlpatterns = [
    path('', DiaryView.as_view()),
]
