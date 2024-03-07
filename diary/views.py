from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from diary.models import Diary, Sentences, Keywords, Questions
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

        content = request.get('content')

        # Diary 객체 생성
        newDiary = Diary.objects.create(user=findUser, title=request.get('title'), createDate=request.get('date'), content=content)

        # 키워드 추출
        memory = TextRank(content=content)

        if memory is None:
            return ApiResponse.on_success(
                result=DiarySerializer(newDiary).data,
                response_status=status.HTTP_201_CREATED
            )
        
        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, keyword = make_quiz(memory, keyword_size=5)

        # 각 키워드별로 Question 생성
        for q, k in zip(question, keyword):
            newKeyword = Keywords.objects.create(keyword=k, sentence=memory.sentences)
            Questions.objects.create(question=q, keyword=newKeyword)

        return ApiResponse.on_success(
            result=SentenceSimpleSerializer(newDiary).data,
            response_status=status.HTTP_201_CREATED
        )


class UpdateView(APIView):
    @swagger_auto_schema(operation_description="일기 수정", request_body=UpdateRequest, responses={"201": '작성 성공'})
    def patch(self, request):
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

        # Diary 삭제
        findDiary.delete()

        # user 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        content = request.get('content')

        # Diary 객체 생성
        updateDiary = Diary.objects.create(user=findUser, title=request.get('title'), writedate=request.get('date'), content=content)

        # 키워드 추출
        memory = TextRank(content=content)
        
        if memory is None:
            return ApiResponse.on_success(
                result=DiarySerializer(updateDiary).data,
                response_status=status.HTTP_201_CREATED
            )
        
        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, keyword = make_quiz(memory, keyword_size=5)

        # 각 키워드별로 Question 생성
        for q, k in zip(question, keyword):
            newKeyword = Keywords.objects.create(keyword=k, sentence=memory.sentences)
            Questions.objects.create(question=q, keyword=newKeyword)

        return ApiResponse.on_success(
            result=DiarySerializer(updateDiary).data,
            response_status=status.HTTP_201_CREATED
        )


class GetDiaryByUserView(APIView):
    @swagger_auto_schema(operation_description="유저의 일기 조회", query_serializer=GetUserRequest,
                         response={"200": DiaryResultResponse})
    def get(self, request):
        requestSerial = GetUserRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # User 가져오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        # User와 연관된 모든 Diary 가져오기
        findDiaries = Diary.objects.filter(user=findUser)

        serialized_diaries = []
        for diary in findDiaries:
            serialized_diary = DiaryResultResponse({
                'diaryId': diary.id,
                'title': diary.title,
                'createDate': diary.createDate,
                'content': diary.content,
            })
            serialized_diaries.append(serialized_diary.data)

        return ApiResponse.on_success(
            result=serialized_diaries,
            response_status=status.HTTP_200_OK
        )


class GetQuizView(APIView):
    @swagger_auto_schema(operation_description="일기회상 퀴즈", query_serializer=GetDiaryRequest,
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

        keywords = findDiary.keywords.all()

        # 모든 Sentence 와 연관된 Question 가져오기
        question_keyword = []
        
        for keyword in keywords:
            question_keyword.append({
                "Q": keyword.questions.first().question,
                "A": keyword.keyword
            })

        return ApiResponse.on_success(
            result=question_keyword,
            response_status=status.HTTP_200_OK
        )

class GetDiaryByDateView(APIView):
    @swagger_auto_schema(operation_description="날짜로 일기 검색", query_serializer=GetDiaryByDateRequest,
                         responses={"200": "일기"})
    def get(self, request):
        requestSerial = GetDiaryByDateRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # User 불러오기
        user_id = request.get('userId')
        findUser = User.objects.get(id=user_id)

        diary_date = request.get('date')
        findDiary = Diary.objects.get(user=findUser, writedate = diary_date)

        return ApiResponse.on_success(
            result=DiarySerializer(findDiary).data,
            response_status=status.HTTP_200_OK
        )