from django.db import transaction
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from config.settings import REQUEST_BODY, REQUEST_PATH
from users.serializers.user_get_post_put_delete_serializers import *
from users.token_handler import token_permission_validator


class GetUsersAndUpdateView(APIView):
    @swagger_auto_schema(
        operation_id="회원 목록 출력",
        operation_description="`개발용` \n회원 목록 출력",
        security=[],
        responses={
            status.HTTP_200_OK:
                ApiResponse.schema(UserSerializer, many=True)
        }
    )
    def get(self, request: Request) -> HttpResponse:
        findUsers = User.objects.all()
        return ApiResponse.on_success(
            UserSerializer(findUsers, many=True).data,
            response_status=status.HTTP_200_OK
        )

    @transaction.atomic
    @swagger_auto_schema(
        operation_id="유저 수정", request_body=UserUpdateRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(UserSerializer)},
        security=[{'AccessToken': []}]
    )
    @token_permission_validator(where_is_userId=REQUEST_BODY, userIdName='id')
    @validator(request_serializer=UserUpdateRequest, request_type=REQUEST_BODY, return_key='serializer')
    def put(self, request):
        updateSerializer = request.serializer
        updateRequest = updateSerializer.validated_data

        findUser = User.objects.get(id=updateRequest['id'])

        updateSerializer.update(findUser, updateRequest)

        return ApiResponse.on_success(
            result=UserSerializer(findUser).data
        )


class GetUserAndDeleteView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_id="유저 조회",
                         responses={status.HTTP_200_OK: ApiResponse.schema(UserSerializer, description="유저 조회")},
                         security=[{'AccessToken': []}])
    @token_permission_validator(where_is_userId=REQUEST_PATH)
    @validator(request_type=REQUEST_PATH, request_serializer=UserIdReqeust, return_key='serializer')
    def get(self, request, userId: int):
        findUser = User.objects.get(id=userId)
        return ApiResponse.on_success(
            result=UserSerializer(findUser).data
        )

    @transaction.atomic
    @swagger_auto_schema(
        operation_id="유저 삭제",
        responses={status.HTTP_200_OK: ApiResponse.schema(ApiResponse)},
        security=[{'AccessToken': []}]
    )
    @token_permission_validator(where_is_userId=REQUEST_PATH)
    @validator(request_serializer=UserIdReqeust, request_type=REQUEST_PATH, return_key='serializer')
    def delete(self, request, userId: int):
        User.objects.get(id=userId).delete()
        return ApiResponse.on_success(
            message="삭제 완료"
        )
