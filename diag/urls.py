from django.urls import path

from diag.views import *

urlpatterns = [
    path('/record', RecordView.as_view()),
]
