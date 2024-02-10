from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from users.serializers import UserSerializer, UserCreateRequest, SigninResponse, LoginResponse, LoginRequest

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
    @swagger_auto_schema(operation_description="회원가입", request_body=UserSerializer, responses={"201":SigninResponse})
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        result = []

        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            if User.objects.filter(username=username).exists():
                return Response({'message' : '이미 가입된 사용자입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({'message' : '이미 사용 중인 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            result.append({
                'username' : username,
                'password' : password
            })

            return Response({'isSucces' : 'True', 'result' : result}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    @swagger_auto_schema(operation_description="로그인", request_body=LoginRequest, responses={"200":LoginResponse})
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
