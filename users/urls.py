from django.urls import path

from .views import UserView, SigninView

urlpatterns = [
    path('', UserView.as_view()),
    path('signin', SigninView.as_view())
]
