from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiaryView, WriteView

urlpatterns = [
    path('', DiaryView.as_view()),
    path('write', WriteView.as_view())
]
