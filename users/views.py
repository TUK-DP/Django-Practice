from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from users.serializers import UserSerializer, UserCreateRequest, UserResponse, LoginRequest, DeleteRequest, UpdateResquest

from drf_yasg.utils import swagger_auto_schema

import json


class UserView(APIView):
    def get(self, request: WSGIRequest) -> HttpResponse:
        findUsers = User.objects.all()
        serializer = UserSerializer(findUsers, many=True)
        return JsonResponse(serializer.data, safe=False)

    @csrf_exempt
    def post(self, request: WSGIRequest) -> HttpResponse:
        data = JSONParser().parse(request)
        request = UserCreateRequest(data=data)
        if request.is_valid():
            newUser = request.to_user()
            return JsonResponse(newUser.data, status=201)
        return JsonResponse(request.errors, status=400)
        

class SignupView(APIView):
    @swagger_auto_schema(operation_description="회원가입", request_body=UserSerializer, responses={"201":UserResponse})
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        result = []

        if serializer.is_valid():
            nickname = serializer.validated_data.get('nickname')
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            serializer.save()

            user_json = UserSerializer(User.objects.get(nickname=nickname))

            return JsonResponse({'isSuccess' : True, 'result' : user_json.data}, status=status.HTTP_201_CREATED)
        
        return JsonResponse({'isSuccess' : False, 'message' : '입력하지 않은 정보가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    

class SigninView(APIView):
    @swagger_auto_schema(operation_description="로그인", request_body=LoginRequest, responses={"200":UserResponse})
    def post(self, request):
        serializer = LoginRequest(data=request.data)
        result = []

        if not serializer.is_valid():
            return JsonResponse({'isSuccess' : False, 'message': '아이디와 비밀번호를 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        nickname = serializer.validated_data.get('nickname')
        password = serializer.validated_data.get('password')

        if User.objects.filter(nickname=nickname, password=password).exists():
            user_json = UserSerializer(User.objects.get(nickname=nickname))

            return JsonResponse({'isSuccess' : True, 'result' : user_json.data}, status=status.HTTP_201_CREATED)
            
        return JsonResponse({'isSuccess' : False, 'message' : '아이디나 비밀번호를 다시 확인해주세요.'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteView(APIView):
    @swagger_auto_schema(operation_description="유저 삭제", request_body=DeleteRequest, responses={"200":'삭제 완료'})
    def delete(self, request):
        serializer = DeleteRequest(data=request.data)

        if serializer.is_valid():
            nickname = serializer.validated_data.get('nickname')

            if User.objects.filter(nickname=nickname).exists():
                delete_user = User.objects.get(nickname=nickname)
                delete_user.delete()
                return JsonResponse({'isSuccess' : True, 'message' : '삭제되었습니다.'}, status=status.HTTP_200_OK)
            
        return JsonResponse({'isSuccess' : False, 'message' : '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    

class UpdateView(APIView):
    @swagger_auto_schema(operation_description="유저 정보 수정", request_body=UpdateResquest, responses={"200":UserResponse})
    def patch(self, request):
        serializer = UpdateResquest(data=request.data)

        if serializer.is_valid():
            id = serializer.validated_data.get('id')
            nickname = serializer.validated_data.get('nickname')
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            try:
                updateuser = User.objects.get(id=id)

                if(updateuser.nickname != nickname):
                    if User.objects.filter(nickname=nickname).exists():
                        return JsonResponse({'isSuccess' : False, 'message': '중복된 아이디입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                updateuser.nickname = nickname

                if(updateuser.email != email):
                    if User.objects.filter(email=email).exists():
                        return JsonResponse({'isSuccess' : False, 'message': '중복된 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)
                updateuser.email = email

                updateuser.username = username
                updateuser.password = password

                updateuser.save()

                user_json = UserSerializer(updateuser)

                return JsonResponse({'isSuccess' : True, 'result' : user_json.data}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'isSuccess' : False, 'message' : '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
        return JsonResponse({'isSuccess' : False, 'message' : '입력한 값을 다시 확인해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

