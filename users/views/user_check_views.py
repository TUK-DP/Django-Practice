from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from users.serializers import *


class CheckNicknameView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="닉네임 중복 확인", request_body=DuplicateNicknameRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(ApiResponse, description="사용가능한 닉네임")},
        security=[]
    )
    @validator(request_serializer=DuplicateNicknameRequest)
    def post(self, request):
        return ApiResponse.on_success(
            response_status=status.HTTP_200_OK,
            message="사용가능한 닉네임입니다.",
        )


class CheckEmailView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="이메일 중복 확인", request_body=DuplicateEmailRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(ApiResponse, description="사용가능한 이메일")},
        security=[]
    )
    @validator(request_serializer=DuplicateEmailRequest)
    def post(self, request):
        return ApiResponse.on_success(
            response_status=status.HTTP_200_OK,
            message="사용가능한 이메일입니다.",
        )
