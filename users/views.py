from django.db import transaction
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_BODY, REQUEST_HEADER, REQUEST_PATH
from users.serializers import *
from users.token_handler import create_token, token_permission_validator, auto_login
from users.token_serializer import AutoLoginRequest


class UserListView(APIView):
    @swagger_auto_schema(
        operation_id="회원 목록 출력",
        operation_description="`개발용` \n"
                              "회원 목록 출력",
        security=[],
    )
    def get(self, request: Request) -> HttpResponse:
        findUsers = User.objects.all()
        return ApiResponse.on_success(
            UserSerializer(findUsers, many=True).data,
            response_status=status.HTTP_200_OK
        )


class UserView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="유저 조회", responses={200: '성공'}, security=[{'AccessToken': []}])
    @token_permission_validator(where_is_userId=REQUEST_PATH)
    @validator(request_type=REQUEST_PATH, request_serializer=UserIdRequire, return_key='serializer')
    def get(self, request, userId: int):
        findUser = User.objects.get(id=userId)
        return ApiResponse.on_success(
            result=UserSerializer(findUser).data
        )

    @transaction.atomic
    @swagger_auto_schema(operation_id="유저 수정", request_body=UserUpdateRequest, responses={200: '성공'}
        , security=[{'AccessToken': []}])
    @token_permission_validator(where_is_userId=REQUEST_PATH)
    @validator(request_serializer=UserUpdateRequest, request_type=REQUEST_BODY, return_key='serializer')
    @validator(request_serializer=UserIdRequire, request_type=REQUEST_PATH, return_key='serializer')
    def patch(self, request, userId: int):
        findUser = User.objects.get(id=userId)
        request.serializer.update(findUser, request.serializer.validated_data)
        return ApiResponse.on_success(
            result=UserSerializer(findUser).data
        )

    @transaction.atomic
    @swagger_auto_schema(operation_id="유저 삭제", responses={200: '삭제 완료'},
                         security=[{'AccessToken': []}])
    @token_permission_validator(where_is_userId=REQUEST_PATH)
    @validator(request_serializer=UserIdRequire, request_type=REQUEST_PATH, return_key='serializer')
    def delete(self, request, userId: int):
        User.objects.get(id=userId).delete()
        return ApiResponse.on_success(
            result="삭제 완료"
        )


class SignupView(APIView):
    # transaction
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="회원 가입",
        operation_description="회원 가입",
        request_body=UserCreateRequest,
        responses={200: "회원 가입 성공"},
        security=[],
    )
    @validator(request_serializer=UserCreateRequest, request_type=REQUEST_BODY, return_key='serializer')
    def post(self, request):
        # User 객체 생성
        return ApiResponse.on_success(
            result=UserSafeSerializer(request.serializer.save()).data,
            response_status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="로그인", request_body=LoginRequest,
                         security=[], )
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


class CheckNicknameView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="닉네임 중복 확인", request_body=DuplicateNicknameRequest,
                         responses={200: '닉네임 사용 가능'}, security=[])
    @validator(request_serializer=DuplicateNicknameRequest)
    def post(self, request):
        return ApiResponse.on_success(
            response_status=status.HTTP_200_OK,
            message="사용가능한 닉네임입니다.",
        )


class AutoLoginView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="자동 로그인", responses={200: '자동 로그인 성공'})
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
