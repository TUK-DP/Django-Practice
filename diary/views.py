from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from diary.models import Diary
from diary.serializers import DiarySerializer, DiaryCreateRequest, WriteRequest
from users.models import User

from drf_yasg.utils import swagger_auto_schema

class DiaryView(APIView):
    def get(self, request: WSGIRequest) -> HttpResponse:
        findDiaries = Diary.objects.all()
        serializer = DiarySerializer(findDiaries, many=True)
        return JsonResponse(serializer.data, safe=False)

    @csrf_exempt
    def post(self, request: WSGIRequest) -> HttpResponse:
        data = JSONParser().parse(request)
        request = DiaryCreateRequest(data=data)
        is_valid = request.is_valid()
        print(request.data)
        if is_valid:
            findUser = User.objects.get(pk=request.data["userId"])
            newDiary = request.to_diary(findUser)

            return JsonResponse(newDiary.data, status=201)
        else:
            return JsonResponse(DiarySerializer(data=data).errors, status=400)


class WriteView(APIView):
    @swagger_auto_schema(operation_description="일기 작성", request_body=WriteRequest, responses={"201":'작성 성공'})
    def post(self, request):
        serializer = WriteRequest(data=request.data)
        result = []

        if serializer.is_valid():
            userId = serializer.validated_data.get('userId')
            title = serializer.validated_data.get('title')
            content = serializer.validated_data.get('content')
            
            user = User.objects.get(id=userId)

            if user is not None:
                serializer.save()

                result.append({
                    'userId' : userId,
                    'title' : title,
                    'content' : content
                })

                return Response({'isSuccess' : True, 'result' : result}, status=status.HTTP_201_CREATED)

            return Response({'isSuccess' : False, 'message' : '사용자를 찾을 수 없습니다.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)