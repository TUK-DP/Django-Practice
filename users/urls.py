from django.urls import path

from .views import UserView, SignupView, SigninView, DeleteView, UpdateView, CheckNicknameView, RecordSaveView, GetDiagRecordView

urlpatterns = [
    path('', UserView.as_view()),
    path('signup', SignupView.as_view()),
    path('signin', SigninView.as_view()),
    path('delete', DeleteView.as_view()),
    path('update', UpdateView.as_view()),
    path('checknickname', CheckNicknameView.as_view()),
    path('recordsave', RecordSaveView.as_view()),
    path('prevrecord', GetDiagRecordView.as_view())
]
