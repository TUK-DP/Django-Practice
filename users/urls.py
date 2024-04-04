from django.urls import path

from .views import UserView, SignupView, SigninView, DeleteView, UpdateView, CheckNicknameView

urlpatterns = [
    path('', UserView.as_view()),
    path('signup', SignupView.as_view()),
    path('signin', SigninView.as_view()),
    path('delete', DeleteView.as_view()),
    path('update', UpdateView.as_view()),
    path('checknickname', CheckNicknameView.as_view())
]
