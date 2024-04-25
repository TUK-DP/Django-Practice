from django.urls import path
from .views import *

urlpatterns = [
    path('', UserListView.as_view()),
    path('/signup', SignupView.as_view()),
    path('/login', LoginView.as_view()),
    path('/<int:userId>/auto/login', AutoLoginView.as_view()),
    path('/<int:userId>', UserView.as_view()),
    path('/checknickname', CheckNicknameView.as_view())
]
