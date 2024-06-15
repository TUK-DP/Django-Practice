from django.urls import path

from users.views.user_check_views import *

from users.views.user_diag_views import *
from users.views.user_get_update_delete_views import *
from users.views.user_login_views import *
from users.views.user_sign_up_views import SignupView

urlpatterns = [
    path('', GetUsersAndUpdateView.as_view()),
    path('/signup', SignupView.as_view()),
    path('/login', LoginView.as_view()),
    path('/<int:userId>/auto/login', AutoLoginView.as_view()),
    path('/<int:userId>', GetUserAndDeleteView.as_view()),
    path('/checknickname', CheckNicknameView.as_view()),
    path('/recordsave', RecordSaveView.as_view()),
    path('/prevrecord', GetDiagRecordView.as_view()),
    path('/checkemail', CheckEmailView.as_view())
]
