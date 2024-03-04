from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiaryView, WriteView, GetDiarybyUserView, GetQuizView, UpdateView

urlpatterns = [
    path('', DiaryView.as_view()),
    path('write', WriteView.as_view()),
    path('list', GetDiarybyUserView.as_view()),
    path('quiz', GetQuizView.as_view()),
    path('update', UpdateView.as_view())
]
