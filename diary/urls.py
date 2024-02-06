from django.urls import path
from diary import views

urlpatterns = [
    path('', views.findAll),
    path('save', views.save),
]
# users/ 요청이 오면 view.py의 index함수를 실행!