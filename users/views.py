from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from users.models import User
from users.serializers import UserSerializer, UserResponse, LoginRequest, NicknameRequest, \
    UpdateResquest, UserIdReqeust


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

        try:
            user = User.objects.get(nickname=request.get('nickname'), password=request.get('password'))
        except User.DoesNotExist:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        return ApiResponse.on_success(
            result=UserSerializer(user).data,
            response_status=status.HTTP_201_CREATED
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

        user = User.objects.get(id=request.get('userId'))
        user.isDeleted = True
        User.save(user)

        return ApiResponse.on_success(
            result=UserSerializer(user).data,
            response_status=status.HTTP_201_CREATED
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
        serializer = UpdateResquest(data=request.data)

        if serializer.is_valid():
            nickname = serializer.validated_data.get('nickname')
            email = serializer.validated_data.get('email')

            try:
                updateuser = User.objects.get(id=serializer.validated_data.get('id'))

                if (updateuser.nickname != nickname):
                    if User.objects.filter(nickname=nickname).exists():
                        return JsonResponse({'isSuccess': False, 'message': '중복된 아이디입니다.'},
                                            status=status.HTTP_400_BAD_REQUEST)
                updateuser.nickname = nickname

                if (updateuser.email != email):
                    if User.objects.filter(email=email).exists():
                        return JsonResponse({'isSuccess': False, 'message': '중복된 이메일입니다.'},
                                            status=status.HTTP_400_BAD_REQUEST)
                updateuser.email = email

                updateuser.username = serializer.validated_data.get('username')
                updateuser.password = serializer.validated_data.get('password')

                updateuser.save()

                return JsonResponse({'isSuccess': True, 'result': UserSerializer(updateuser).data},
                                    status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'isSuccess': False, 'message': '사용자를 찾을 수 없습니다.'},
                                    status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'isSuccess': False, 'message': '입력한 값을 다시 확인해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
