from django.urls import path

from diary.views.quiz_views import GetQuizView

urlpatterns = [
    path('', GetQuizView.as_view()),
]
