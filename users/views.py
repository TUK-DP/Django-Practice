from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from users.serializers import *


class UserView(APIView):
    @swagger_auto_schema(
        operation_id="회원 목록 출력",
        operation_description="`개발용` \n"
                              "회원 목록 출력"
    )
    def get(self, request: WSGIRequest) -> HttpResponse:
        findUsers = User.objects.all()
        return ApiResponse.on_success(
            UserSerializer(findUsers, many=True).data,
            response_status=status.HTTP_200_OK
        )


class SignupView(APIView):
    # transaction
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="회원 가입",
        operation_description="회원 가입",
        request_body=UserCreateRequest,
        responses={200: "회원 가입 성공"}
    )
    @validator(request_serializer=UserCreateRequest)
    def post(self, request):
        requestSerial = UserCreateRequest(data=request.data)
        requestSerial.is_valid()

        # User 객체 생성
        return ApiResponse.on_success(
            result=UserSafeSerializer(requestSerial.save()).data,
            response_status=status.HTTP_201_CREATED
        )


class SigninView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="로그인", request_body=LoginRequest)
    @validator(request_serializer=LoginRequest)
    def post(self, request):
        requestSerializer = LoginRequest(data=request.data)
        requestSerializer.is_valid()

        findUser = User.objects.get(
            email=requestSerializer.validated_data.get('email'),
            password=requestSerializer.validated_data.get('password')
        )

        return ApiResponse.on_success(
            result=UserSerializer(findUser).data,
            response_status=status.HTTP_200_OK
        )


class DeleteView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="유저 삭제", request_body=UserDeleteRequest, responses={200: '삭제 완료'})
    @validator(request_serializer=UserDeleteRequest)
    def delete(self, request):
        requestSerializer = UserDeleteRequest(data=request.data)
        requestSerializer.is_valid()

        User.objects.get(id=request.data.get('id')).delete()

        return ApiResponse.on_success(
            result="삭제 완료"
        )


class CheckNicknameView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="닉네임 중복 확인", request_body=DuplicateNicknameRequest, responses={200: '닉네임 사용 가능'})
    @validator(request_serializer=DuplicateNicknameRequest)
    def post(self, request):
        requestSerializer = DuplicateNicknameRequest(data=request.data)
        requestSerializer.is_valid()

        return ApiResponse.on_success(
            response_status=status.HTTP_200_OK,
            message="사용가능한 닉네임입니다.",
        )


class UpdateView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="유저 정보 수정", request_body=UserUpdateRequest)
    @validator(request_serializer=UserUpdateRequest)
    def patch(self, request):
        requestSerializer = UserUpdateRequest(data=request.data)
        requestSerializer.is_valid()
        body = request.data

        findUser = User.objects.get(id=body.get('id'))

        fields = requestSerializer.get_fields()

        for filed in fields:
            if filed in body:
                setattr(findUser, filed, body.get(filed))

        findUser.save()

        return ApiResponse.on_success(
            result=UserSerializer(findUser).data,
            response_status=status.HTTP_200_OK
        )
