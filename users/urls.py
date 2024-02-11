from django.urls import path

from .views import UserView, SigninView, LoginView, DeleteView, UpdateView

urlpatterns = [
    path('', UserView.as_view()),
    path('signin', SigninView.as_view()),
    path('login', LoginView.as_view()),
    path('delete', DeleteView.as_view()),
    path('update', UpdateView.as_view())
]
