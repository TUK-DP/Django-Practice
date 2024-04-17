from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from users.models import User, DiagRecord
from users.serializers import UserSerializer, UserResponse, LoginRequest, NicknameRequest, \
    UpdateResquest, UserIdReqeust, RecordSaveRequest, DiagRecordSerializer


class UserView(APIView):
    def get(self, request: WSGIRequest) -> HttpResponse:
        findUsers = User.objects.all()
        return ApiResponse.on_success(
            UserSerializer(findUsers, many=True).data,
            response_status=status.HTTP_200_OK
        )


class SignupView(APIView):
    # transaction
    @transaction.atomic
    @swagger_auto_schema(operation_description="회원가입", request_body=UserSerializer, responses={201: UserResponse})
    def post(self, request):
        requestSerial = UserSerializer(data=request.data)

        # 유효성 검사 통과하지 못한 경우
        if not requestSerial.is_valid():
            return ApiResponse.on_fail(
                requestSerial.errors,
                response_status=status.HTTP_400_BAD_REQUEST
            )

        # 유효성 검사 통과한 경우
        # User 객체 생성
        newUser = requestSerial.save()
        return ApiResponse.on_success(
            result=UserSerializer(newUser).data,
            response_status=status.HTTP_201_CREATED
        )


class SigninView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="로그인", request_body=LoginRequest, responses={200: UserResponse})
    def post(self, request):
        requestSerial = LoginRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        user = User.objects.filter(nickname=request.get('nickname'), 
                                    password=request.get('password'),
                                    isDeleted='False')
        
        if not user.exists():
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        return ApiResponse.on_success(
            result=UserSerializer(user).data,
            response_status=status.HTTP_200_OK
        )


class DeleteView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="유저 삭제", request_body=UserIdReqeust, responses={200: '삭제 완료'})
    def delete(self, request):
        requestSerial = UserIdReqeust(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        user = User.objects.get(id=request.get('userId'), isDeleted='False')
        user.isDeleted = True
        User.save(user)

        return ApiResponse.on_success(
            result=UserSerializer(user).data,
            response_status=status.HTTP_200_OK
        )


class CheckNicknameView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="닉네임 중복확인", request_body=NicknameRequest, responses={200: '닉네임 사용 가능'})
    def post(self, request):
        requestSerial = NicknameRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        result = []
        result.append({
            "nickname": request.get('nickname')
        })

        return ApiResponse.on_success(
            message="사용가능한 닉네임입니다.",
            result=result,
            response_status=status.HTTP_200_OK
        )


class UpdateView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="유저 정보 수정", request_body=UpdateResquest, responses={"200": UserResponse})
    def patch(self, request):
        requestSerial = UpdateResquest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        updateUser = User.objects.filter(id=request.get('userId'), isDeleted='False').first()

        updateUser.username = request.get('username')
        updateUser.nickname = request.get('nickname')
        updateUser.email = request.get('email')
        updateUser.password = request.get('password')
        updateUser.birth = request.get('birth')

        User.save(updateUser)

        return ApiResponse.on_success(
            result=UserSerializer(updateUser).data,
            response_status=status.HTTP_200_OK
        )
    

class RecordSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="치매진단 결과 저장", request_body=RecordSaveRequest, responses={200: '닉네임 사용 가능'})
    def post(self, request):
        requestSerial = RecordSaveRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # 유효성 검사 통과한 경우
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
    def get(self, request):
        requestSerial = UserIdReqeust(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        diagRecord = DiagRecord.objects.filter(user=User.objects.get(id=request.get('userId'), isDeleted='False')).order_by('-created_at').first()

        return ApiResponse.on_success(
            result=DiagRecordSerializer(diagRecord).data,
            response_status=status.HTTP_200_OK
        )