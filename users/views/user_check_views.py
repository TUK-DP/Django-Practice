from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from users.serializers.user_check_serializers import *


class CheckAccountIdView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="회원가입시 아이디 중복 확인", request_body=DuplicateAccountIdRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(ApiResponse, description="사용가능한 아이디")},
        security=[]
    )
    @validator(request_serializer=DuplicateAccountIdRequest)
    def post(self, request):
        return ApiResponse.on_success(
            response_status=status.HTTP_200_OK,
            message="사용가능한 아이디입니다.",
        )