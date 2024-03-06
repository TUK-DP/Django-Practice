from django.urls import path
from .views import WriteView, GetDiarybyUserView, GetQuizView, UpdateView

urlpatterns = [
    path('write', WriteView.as_view()),
    path('list', GetDiarybyUserView.as_view()),
    path('quiz', GetQuizView.as_view()),
    path('update', UpdateView.as_view())
]
