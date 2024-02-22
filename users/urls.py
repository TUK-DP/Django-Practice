from django.urls import path

from .views import UserView, SignupView, SigninView, DeleteView, UpdateView

urlpatterns = [
    path('', UserView.as_view()),
    path('signup', SignupView.as_view()),
    path('signin', SigninView.as_view()),
    path('delete', DeleteView.as_view()),
    path('update', UpdateView.as_view())
]
