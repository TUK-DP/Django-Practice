from django.urls import path

from diary.views.keyword_views import *

urlpatterns = [
    path('/diary/<int:diaryId>', GetKeywordView.as_view()),
    path('/<int:keywordId>/image', KeywordImgSaveView.as_view()),
]
