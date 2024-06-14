from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from config.settings import REQUEST_BODY, REQUEST_HEADER, REQUEST_PATH
from users.serializers import *
from users.token_handler import create_token, token_permission_validator, auto_login
from users.token_serializer import AutoLoginRequest


class LoginView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="로그인",
        request_body=LoginRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(serializer_class=LoginResponse, description="로그인 성공")},
        security=[]
    )
    @validator(request_serializer=LoginRequest, request_type=REQUEST_BODY, return_key="serializer")
    def post(self, request):
        findUser = User.objects.get(
            email=request.serializer.data.get('email'),
            password=request.serializer.data.get('password')
        )

        # 토큰 생성
        token_serial = create_token(findUser.id)

        # 토큰 저장
        findUser.refresh_token = token_serial.data.get('RefreshToken')
        findUser.save()

        # 응답 생성
        response = LoginResponse(data={
            "user": UserSerializer(findUser).data,
            "token": token_serial.data
        })

        response.is_valid()

        return ApiResponse.on_success(
            result=response.data,
            response_status=status.HTTP_200_OK
        )


class AutoLoginView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="자동 로그인",
        responses={
            status.HTTP_200_OK: ApiResponse.schema(LoginResponse, description="자동 로그인 성공")}
    )
    @token_permission_validator(where_is_userId=REQUEST_PATH)
    @validator(request_serializer=TokenSerializer, request_type=REQUEST_HEADER, return_key="token")
    @validator(request_serializer=AutoLoginRequest, request_type=REQUEST_PATH)
    def get(self, request, userId):
        is_valid, message, token = auto_login(userId, request.token)

        # 만료 되거나 decoding 이 안되는 유효하지 않은 토큰이라면 실패 응답 반환
        if not is_valid:
            return ApiResponse.on_fail(
                message,
                response_status=status.HTTP_403_FORBIDDEN
            )

        findUser = User.objects.get(id=userId)
        response = LoginResponse(data={
            "user": UserSerializer(findUser).data,
            "token": token.data
        })

        response.is_valid()
        return ApiResponse.on_success(
            result=response.data,
            response_status=status.HTTP_200_OK
        )
