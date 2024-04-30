from django.urls import path

from .views import *

urlpatterns = [
    path('', DiaryCreateView.as_view()),
    path('/<int:diaryId>/image', DiaryImgSaveView.as_view()),
    path('/<int:diaryId>', DiaryCRUDView.as_view()),
    path('/<int:diaryId>/graph', GetNodeData.as_view()),
    path('/user/<int:userId>', GetDiaryByUserView.as_view()),
    path('/checkanswer', CheckAnswerView.as_view()),
]
