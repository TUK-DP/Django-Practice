from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


schema_view = get_schema_view(
    openapi.Info(
        title="DP API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/diary', include('diary.urls.diary_urls')),
    path('api/keyword', include('diary.urls.keyword_urls')),
    path('api/quiz', include('diary.urls.quiz_urls')),
    path('api/users', include('users.urls')),
    path('api/image', include('image.urls')),
    path('api/center', include('center.urls')),

    re_path(r'^api/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='api2/schema-swagger-ui'),
]

urlpatterns += staticfiles_urlpatterns()