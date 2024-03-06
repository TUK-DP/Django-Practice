from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from diary.serializers import *
from users.models import User
from .textrank import TextRank, make_quiz


class WriteView(APIView):
    @swagger_auto_schema(operation_description="일기 작성", request_body=WriteRequest, responses={"201": '작성 성공'})
    def post(self, request):
        requestSerial = WriteRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # user 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        # Diary 객체 생성
        newDiary = Diary.objects.create(user=findUser, title=request.get('title'))

        sentence = request.get('content')

        # Sentences 객체 생성
        newSentence = Sentences.objects.create(sentence=sentence, diary=newDiary)

        # 키워드 추출
        memory = TextRank(content=sentence)

        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, answer = make_quiz(memory, keyword_size=5)

        # Quizs 객체 생성
        Quizs.objects.bulk_create(
            [Quizs(question=q, answer=a, sentence=newSentence) for q, a in zip(question, answer)]
        )

        return ApiResponse.on_success(
            result=SentenceSimpleSerializer(newSentence).data,
            response_status=status.HTTP_201_CREATED
        )


class UpdateView(APIView):
    @swagger_auto_schema(operation_description="일기 수정", request_body=UpdateRequest, responses={"201": '작성 성공'})
    def post(self, request):
        requestSerial = UpdateRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # Diary 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        # Diary와 연관된 모든 Sentence 삭제
        findDiary.sentences.all().delete()

        content = request.get('content')
        newSentence = Sentences.objects.create(sentence=content, diary=findDiary)

        memory = TextRank(content=content)
        question, answer = make_quiz(memory, keyword_size=5)

        Quizs.objects.bulk_create(
            [Quizs(question=q, answer=a, sentence=newSentence) for q, a in zip(question, answer)]
        )

        return ApiResponse.on_success(
            result=SentenceSimpleSerializer(newSentence).data,
            response_status=status.HTTP_201_CREATED
        )


class GetDiarybyUserView(APIView):
    @swagger_auto_schema(operation_description="유저의 일기 조회", query_serializer=GetUserRequest,
                         responses={"200": DiarySerializer})
    def get(self, request):
        serializer = GetUserRequest(data=request.query_params)

        if serializer.is_valid():
            try:
                user = User.objects.get(id=serializer.validated_data.get('userId'))
                diaries = Diary.objects.filter(user=user)
                serializer = DiarySerializer(diaries, many=True)
                return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'isSuccess': False, 'message': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetQuizView(APIView):
    @swagger_auto_schema(operation_description="일기회상 퀴즈", query=GetDiaryRequest,
                         responses={"200": "퀴즈"})
    def get(self, request):
        requestSerial = GetDiaryRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # Diary 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        # Diary와 연관된 모든 Sentence 가져오기
        sentences = findDiary.sentences.all()

        # 모든 Sentence와 연관된 Quiz 가져오기 == [Quizs, Quizs, Quizs, ...]
        quizzes = sum([sentence.quizs.all() for sentence in sentences], [])

        return ApiResponse.on_success(
            result=QuizSerializer(quizzes, many=True).data,
            response_status=status.HTTP_200_OK
        )

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
