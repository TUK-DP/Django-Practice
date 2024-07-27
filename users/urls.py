from django.urls import path

from users.views.user_check_views import *

from users.views.user_diag_views import *
from users.views.user_get_update_delete_views import *
from users.views.user_login_views import *
from users.views.user_join_views import *

urlpatterns = [
    path('', GetUsersAndUpdateView.as_view()),
    path('/signup', SignupView.as_view()),
    path('/login', LoginView.as_view()),
    path('/<int:userId>/auto/login', AutoLoginView.as_view()),
    path('/<int:userId>', GetUserAndDeleteView.as_view()),
    path('/validate/accountId', CheckAccountIdView.as_view()),
    path('/recordsave', RecordSaveView.as_view()),
    path('/prevrecord', GetDiagRecordView.as_view()),
]
