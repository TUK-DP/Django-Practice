from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from diary.models import Diary
from diary.serializers import DiarySerializer, DiaryCreateRequest, WriteRequest, GetDiaryRequest, GetUserRequest
from users.models import User

from drf_yasg.utils import swagger_auto_schema

from . import textrank

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
            user = User.objects.get(id=serializer.validated_data.get('userId'))

            if user is not None:
                diary = serializer.save()
                return JsonResponse({'isSuccess' : True, 'result' : DiarySerializer(diary).data}, status=status.HTTP_201_CREATED)
            
            return JsonResponse({'isSuccess' : False, 'message' : '사용자를 찾을 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)   
             
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
            diaryId = serializer.validated_data.get('diaryId')
            try:
                diary = Diary.objects.get(id=diaryId)
                content = diary.content

                diary_sentences = textrank.get_text(content)
                nouns = textrank.get_nouns(diary_sentences)
                sent_graph = textrank.build_sent_graph(nouns)
                words_graph, idx2word = textrank.build_words_graph(nouns)
                sent_rank_idx = textrank.get_ranks(sent_graph)
                sorted_sent_rank_idx = sorted(sent_rank_idx, key=lambda k: sent_rank_idx[k], reverse=True)
                word_rank_idx = textrank.get_ranks(words_graph)
                sorted_word_rank_idx = sorted(word_rank_idx, key=lambda k: word_rank_idx[k], reverse=True)
                summary_sentence = textrank.summarize(sorted_sent_rank_idx, diary_sentences)
                summary_key = textrank.keywords(sorted_word_rank_idx, idx2word)
                question, answer = textrank.make_quiz(summary_sentence, summary_key)

                result = []
                
                for q, a in zip(question, answer):
                    result.append({f'Q{len(result)+1}': q, f'A{len(result)+1}': a})

                return JsonResponse({'isSuccess' : True, 'result' : result}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'isSuccess' : False, 'message' : '사용자를 찾을 수 없습니다.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)