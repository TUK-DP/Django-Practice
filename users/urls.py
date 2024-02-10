from django.urls import path

from .views import UserView, SigninView, LoginView

urlpatterns = [
    path('', UserView.as_view()),
    path('signin', SigninView.as_view()),
    path('login', LoginView.as_view())
]
