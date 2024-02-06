from django.urls import path
from users import views

urlpatterns = [
    path('', views.index),
]
# users/ 요청이 오면 view.py의 index함수를 실행!