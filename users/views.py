from django.db import transaction
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from config.settings import REQUEST_BODY, REQUEST_HEADER, REQUEST_PATH, REQUEST_QUERY
from users.serializers import *
from users.token_handler import create_token, token_permission_validator, auto_login
from users.token_serializer import AutoLoginRequest


class UserListView(APIView):
    @swagger_auto_schema(
        operation_id="회원 목록 출력",
        operation_description="`개발용` \n"
                              "회원 목록 출력",
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


class UserView(APIView):
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


class RecordSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="치매진단 결과 저장", request_body=RecordSaveRequest,
                         responses={200: '닉네임 사용 가능'})
    @validator(request_serializer=RecordSaveRequest, request_type=REQUEST_BODY, return_key="serializer")
    def post(self, request):
        request = request.serializer.validated_data

        # DiagRecord 객체 생성
        diagRecord = DiagRecord.objects.create(
            totalQuestionSize=request.get('totalQuestionSize'),
            yesCount=request.get('yesCount'),
            user=User.objects.get(id=request.get('userId'), isDeleted='False')
        )

        return ApiResponse.on_success(
            result=DiagRecordSerializer(diagRecord).data,
            response_status=status.HTTP_200_OK
        )


class GetDiagRecordView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="유저의 이전 진단 기록 조회", query_serializer=UserIdReqeust,
                         response={"200": DiagRecordSerializer})
    @validator(request_serializer=UserIdReqeust, request_type=REQUEST_QUERY, return_key='serializer')
    def get(self, request):
        request = request.serializer.validated_data

        diagRecord = DiagRecord.objects.filter(
            user=User.objects.get(id=request.get('userId'))).order_by('-created_at').first()

        return ApiResponse.on_success(
            result=DiagRecordSerializer(diagRecord).data,
            response_status=status.HTTP_200_OK
        )
