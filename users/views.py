from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from users.serializers import UserSerializer, UserCreateRequest, UserResponse, LoginResponse, LoginRequest, DeleteRequest

from drf_yasg.utils import swagger_auto_schema


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
        

class SigninView(APIView):
    @swagger_auto_schema(operation_description="회원가입", request_body=UserSerializer, responses={"201":UserResponse})
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        result = []

        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            if(username == None or email == None or password == None):
                return Response({'message': '모든 값이 입력되지 않았습니다'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            result.append({
                'username' : username,
                'password' : password
            })

            return Response({'isSucces' : 'True', 'result' : result}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    @swagger_auto_schema(operation_description="로그인", request_body=LoginRequest, responses={"200":UserResponse})
    def post(self, request):
        serializer = LoginRequest(data=request.data)
        result = []

        if not serializer.is_valid():
            return Response({'message': '아이디와 비밀번호를 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        if User.objects.filter(username=username, password=password).exists():
            result.append({
                'username' : username,
                'password' : password
                })
                    
            return Response({'isSucces' : 'True', 'result' : result}, status=status.HTTP_201_CREATED)
            
        return Response({'message' : '아이디나 비밀번호를 다시 확인해주세요.'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteView(APIView):
    @swagger_auto_schema(operation_description="유저 삭제", request_body=DeleteRequest, responses={"200": '삭제 완료'})
    def delete(self, request):
        serializer = DeleteRequest(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data.get('username')

            if User.objects.filter(username=username).exists():
                delete_user = User.objects.get(username=username)
                delete_user.delete()
                return Response({'message' : '삭제되었습니다.'}, status=status.HTTP_200_OK)
            
        return Response({'message' : '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)