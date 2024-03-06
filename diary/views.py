from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from diary.models import Diary, Sentences, Quizs
from diary.serializers import *
from users.models import User

from drf_yasg.utils import swagger_auto_schema

from .textrank import TextRank, make_quiz

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

        if serializer.is_valid():
            user_id = serializer.validated_data.get('userId')
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'isSuccess': False, 'message': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            diary = Diary.objects.create(user=user, title=serializer.validated_data.get('title'))

            content = serializer.validated_data.get('content')

            if not content or len(content) < 10:
                return JsonResponse({'isSuccess': False, 'message': '적어도 한 문장 이상 작성해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

            sentence = Sentences.objects.create(sentence=content, diary=diary)

            memory = TextRank(content=content)
            question, answer = make_quiz(memory, keyword_size=5)

            Quizs.objects.bulk_create([Quizs(question=q, answer=a, sentence=sentence) for q, a in zip(question, answer)])

            return JsonResponse({'isSuccess': True, 'result': SentenceSimpleSerializer(sentence).data}, status=status.HTTP_201_CREATED)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateView(APIView):
    @swagger_auto_schema(operation_description="일기 수정", request_body=UpdateRequest, responses={"201":'작성 성공'})
    def post(self, request):
        serializer = UpdateRequest(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data.get('userId')
            diary_id = serializer.validated_data.get('diaryId')
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'isSuccess': False, 'message': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                deleteDiary = Diary.objects.get(id=diary_id)
                Diary.delete(deleteDiary)

                diary = Diary.objects.create(user=user, title=serializer.validated_data.get('title'))

                content = serializer.validated_data.get('content')

                sentence = Sentences.objects.create(sentence=content, diary=diary)

                memory = TextRank(content=content)
                question, answer = make_quiz(memory, keyword_size=5)

                Quizs.objects.bulk_create([Quizs(question=q, answer=a, sentence=sentence) for q, a in zip(question, answer)])

                return JsonResponse({'isSuccess': True, 'result': SentenceSimpleSerializer(sentence).data}, status=status.HTTP_201_CREATED)
            except Diary.DoesNotExist:
                return JsonResponse({'isSuccess': False, 'message': '일기를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDiarybyUserView(APIView):
    @swagger_auto_schema(operation_description="유저의 일기 조회", query_serializer=GetUserRequest, responses={"200":DiarySerializer})
    def get(self, request):
        serializer = GetUserRequest(data=request.query_params)

        if serializer.is_valid():
            try:
                user = User.objects.get(id=serializer.validated_data.get('userId'))
                diaries = Diary.objects.filter(user=user)
                serializer = DiarySerializer(diaries, many=True)
                return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'isSuccess' : False, 'message' : '사용자를 찾을 수 없습니다.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class GetQuizView(APIView):
    @swagger_auto_schema(operation_description="일기회상 퀴즈", query_serializer=GetDiaryRequest, responses={"200":"퀴즈"})
    def get(self, request):
        serializer = GetDiaryRequest(data=request.query_params)

        if serializer.is_valid():
            diary_id = serializer.validated_data.get('diaryId')
            try:
                diary = Diary.objects.get(id=diary_id)
            except Diary.DoesNotExist:
                return JsonResponse({'isSuccess': False, 'message': '해당 일기를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

            sentences = diary.sentences.all()
            quizs = []

            for sentence in sentences:
                quizs.extend(sentence.quizs.all())
            
            serializer = QuizSerializer(quizs, many=True)

            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)