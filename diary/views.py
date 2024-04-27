from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse

from config.basemodel import ApiResponse
from diary.serializers import *
from diary.text_rank_modules.textrank import TextRank, make_quiz
from users.models import User
from .graph import GraphDB


class WriteView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기 작성", request_body=WriteRequest, responses={"201": '작성 성공'})
    def post(self, request):
        requestSerial = WriteRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # user 가져오기
        userId = request.get('userId')
        findUser = User.objects.get(id=userId)

        content = request.get('content')

        # Diary 객체 생성
        newDiary = Diary.objects.create(user=findUser, title=request.get('title'), createDate=request.get('date'),
                                        content=content)

        # 키워드 추출
        memory = TextRank(content=content)

        conn = GraphDB()
        conn.create_and_link_nodes(
            user_id=userId, diary_id=newDiary.id,
            words_graph=memory.words_graph,
            words_dict=memory.words_dict,
            weights_dict=memory.weights_dict
        )

        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, keyword = make_quiz(memory, keyword_size=5)

        # 각 키워드별로 Question 생성
        for q, k in zip(question, keyword):
            newKeyword = Keywords.objects.create(keyword=k, diary=newDiary)
            Questions.objects.create(question=q, keyword=newKeyword)

        return ApiResponse.on_success(
            result=DiaryResultResponse(newDiary).data,
            response_status=status.HTTP_201_CREATED
        )


class UpdateView(APIView):
    @transaction.atomic
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
        diaryId = request.get('diaryId')
        findDiary = Diary.objects.get(id=diaryId)

        # Diary 삭제
        findDiary.delete()

        # GraphDB에서도 삭제
        conn = GraphDB()
        conn.delete_diary(user_id=request.get('userId'), diary_id=diaryId)

        # user 가져오기
        userId = request.get('userId')
        findUser = User.objects.get(id=userId)

        content = request.get('content')

        # Diary 객체 생성
        updateDiary = Diary.objects.create(user=findUser, title=request.get('title'), createDate=request.get('date'),
                                           content=content)

        # 키워드 추출
        memory = TextRank(content=content)

        # GraphDB에 추가
        conn.create_and_link_nodes(
            user_id=userId, diary_id=updateDiary.id,
            words_graph=memory.words_graph,
            words_dict=memory.words_dict,
            weights_dict=memory.weights_dict
        )

        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, keyword = make_quiz(memory, keyword_size=5)

        # 각 키워드별로 Question 생성
        for q, k in zip(question, keyword):
            newKeyword = Keywords.objects.create(keyword=k, diary=updateDiary)
            Questions.objects.create(question=q, keyword=newKeyword)

        return ApiResponse.on_success(
            result=DiaryResultResponse(updateDiary).data,
            response_status=status.HTTP_201_CREATED
        )


class GetDiaryByUserView(APIView):
    @transaction.atomic
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
        userId = request.get('userId')
        findUser = User.objects.get(id=userId)

        # User와 연관된 모든 Diary 가져오기
        findDiaries = Diary.objects.filter(user=findUser)

        return ApiResponse.on_success(
            result=DiaryResultResponse(findDiaries, many=True).data,
            response_status=status.HTTP_200_OK
        )


class GetQuizView(APIView):
    @transaction.atomic
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
        diaryId = request.get('diaryId')
        findDiary = Diary.objects.get(id=diaryId)

        keywords = findDiary.keywords.all()

        # 모든 Sentence 와 연관된 Question 가져오기
        result = []

        for keyword in keywords:
            question = keyword.questions.first()
            result.append({
                "questionId": question.pk,
                "question": question.question,
                "keywordId": keyword.id
            })

        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_200_OK
        )


class CheckAnswerView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기회상 답안 확인", request_body=AnswerListRequest,
                         responses={"200": "답안 채점"})
    def post(self, request):
        requestSerial = AnswerListRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data
        
        answers = []
        result = []
        score = 0

        for answerData in request['answers']:
            keywordId = answerData['keywordId']
            answer = answerData['answer']

            keyword = Keywords.objects.get(id=keywordId)
            isCorrect = answer == keyword.keyword
            answers.append({
                'isCorrected': isCorrect,
                'userInput': answer,
                'answer': keyword.keyword,
            })

            if isCorrect:
                score += 1

        result.append({
            "totalQuestionSize": len(request['answers']),
            "score": score,
            "answerList": answers
        })

        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_200_OK
        )

class GetDiaryByDateView(APIView):
    @transaction.atomic
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
        userId = request.get('userId')
        findUser = User.objects.get(id=userId)
        findDiary = Diary.objects.get(user=findUser, createDate=request.get('date'))

        return ApiResponse.on_success(
            result=DiaryResultResponse(findDiary).data,
            response_status=status.HTTP_200_OK
        )


class DeleteDiaryView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기 삭제", request_body=DeleteDiaryRequest,
                         responses={200: '삭제 완료'})
    def delete(self, request):
        requestSerial = DeleteDiaryRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # 다이어리 아이디 가져오기
        diary_id = request.get('diaryId')
        findDiary = Diary.objects.get(id=diary_id)

        Diary.delete(findDiary)

        return ApiResponse.on_success(
            result=DiaryResultResponse(findDiary).data,
            response_status=status.HTTP_200_OK
        )


class GetNodeData(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="노드데이터 가져오기", query_serializer=DeleteDiaryRequest)
    def get(self, request):

        requestSerial = DeleteDiaryRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # 다이어리 아이디 가져오기
        diaryId = request.get('diaryId')
        # 유저 아이디 가져오기
        userId = request.get('userId')

        # 그래프 데이터 가져오기
        conn = GraphDB()
        result = conn.find_all_by_user_diary(userId, diaryId)

        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_200_OK
        )


class KeywordImgSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="키워드별 이미지 저장", request_body=KeyWordImgSaveRequest, responses={"201": '저장 성공'})
    def post(self, request):
        requestSerial = KeyWordImgSaveRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # keyword 객체 가져오기
        keyword = Keywords.objects.get(id=request.get('keywordId'))

        # imgUrl 저장
        keyword.imgUrl = request.get('imgUrl')
        keyword.save()

        return ApiResponse.on_success(
            result=KeywordSerializer(keyword).data,
            response_status=status.HTTP_201_CREATED
        )


class DiaryImgSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기 이미지 저장", request_body=DiaryImgSaveRequest, responses={"201": '저장 성공'})
    def post(self, request):
        requestSerial = DiaryImgSaveRequest(data=request.data)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # keyword 객체 가져오기
        diary = Diary.objects.get(id=request.get('diaryId'))

        # imgUrl 저장
        diary.imgUrl = request.get('imgUrl')
        diary.save()

        return ApiResponse.on_success(
            result=DiaryResultResponse(diary).data,
            response_status=status.HTTP_201_CREATED
        )
    

class KeywordImgPagingView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="키워드별 사진 페이징", query_serializer=FindKeywordImgRequest)
    def get(self, request):
        requestSerial = FindKeywordImgRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        keywordObjects = Keywords.objects.filter(keyword=request.get('keyword'), imgUrl__isnull=False)

        # 필터링된 객체가 없을 경우 404 반환
        if not keywordObjects:
            return ApiResponse.on_fail({"message": "아직 그려진 그림이 없습니다."}, status.HTTP_404_NOT_FOUND)
        
        # 최신순으로 정렬
        keywordObjects = keywordObjects.order_by('-updated_at')

        # imgUrl 필드만 가져와서 리스트로 변환하지 않고 쿼리셋으로 페이지네이션
        keywordImgUrls = keywordObjects.values_list('imgUrl', flat=True)
        requestPage = request.get('page')
        pageSize = request.get('pageSize')

        paginator = Paginator(keywordImgUrls, pageSize)

        try:
            pageObj = paginator.page(requestPage)
        except PageNotAnInteger:
            firstPage = 1
            pageObj = paginator.page(firstPage)
        except EmptyPage:
            lastPage = paginator.num_pages
            pageObj = paginator.page(lastPage)

        result = []

        # JSON 응답 생성
        result.append({
            "isSuccess": True,
            "results": {
                "imgUrls": list(pageObj),
                "totalDataSize": paginator.count,
                "totalPage": paginator.num_pages,
                "hasNext": pageObj.has_next(),
                "hasPrevious": pageObj.has_previous(),
                "currentPage": pageObj.number,
                "dataSize": pageSize
            }
        })

        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_201_CREATED
        )
    

class GetKeywordView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="일기별 키워드 조회", query_serializer=GetDiaryRequest,
                         response={"200": KeywordResultSerializer})
    def get(self, request):
        requestSerial = GetDiaryRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        # 유효성 검사 통과한 경우
        request = requestSerial.validated_data

        # Diary 가져오기
        diary = Diary.objects.get(id=request.get('diaryId'))

        # Diary 연관된 모든 Keyword 가져오기
        findKeywords = Keywords.objects.filter(diary=diary)

        return ApiResponse.on_success(
            result=KeywordResultSerializer(findKeywords, many=True).data,
            response_status=status.HTTP_200_OK
        )