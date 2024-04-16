from django.urls import path
from .views import *

urlpatterns = [
    path('write', WriteView.as_view()),
    path('list', GetDiaryByUserView.as_view()),
    path('quiz', GetQuizView.as_view()),
    path('update', UpdateView.as_view()),
    path('search', GetDiaryByDateView.as_view()),
    path('delete', DeleteDiaryView.as_view()),
    path('graph', GetNodeData.as_view()),
    path('keywordImg', KeywordImgSaveView.as_view()),
    path('diaryImg', DiaryImgSaveView.as_view()),
    path('pagingImg', KeywordImgPagingView.as_view()),
    path('checkanswer', CheckAnswerView.as_view())
]
