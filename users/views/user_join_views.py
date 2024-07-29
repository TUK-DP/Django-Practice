from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from config.settings import REQUEST_BODY
from users.serializers.user_get_post_put_delete_serializers import *


class SignupView(APIView):
    # transaction
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="회원 가입",
        operation_description="회원 가입",
        request_body=UserCreateRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(UserSafeSerializer, description="회원가입 성공")},
        security=[],
    )
    @validator(request_serializer=UserCreateRequest, request_type=REQUEST_BODY, return_key='serializer')
    def post(self, request):
        # User 객체 생성
        return ApiResponse.on_success(
            result=UserSafeSerializer(request.serializer.save()).data,
            response_status=status.HTTP_201_CREATED
        )
