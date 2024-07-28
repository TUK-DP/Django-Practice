from django.urls import path

from diag.views import *

urlpatterns = [
    path('', DiagView.as_view()),
    path('/record', DiagRecordView.as_view())
]
