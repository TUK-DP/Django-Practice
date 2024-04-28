from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_BODY, REQUEST_PATH, REQUEST_QUERY
from diary.serializers import *
from users.models import User
from .graph import GraphDB
from .graph_serializer import GraphDataSerializer


class DiaryCRUDView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기 수정",
        operation_description="일기 수정",
        request_body=DiaryUpdateRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(DiaryResultResponse, description='수정 성공')}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryRequest, return_key='dump')
    @validator(request_type=REQUEST_BODY, request_serializer=DiaryUpdateRequest, return_key='serializer')
    def patch(self, request, diaryId):
        requestSerializer: DiaryUpdateRequest = request.serializer
        request: ReturnDict = requestSerializer.validated_data

        findDiary = Diary.objects.get(id=diaryId)
        # 일기 삭제
        findDiary.delete()

        # GraphDB, 키워드 관련 로직과 같이 일기 생성
        newDiary = Diary.create(
            user=User.objects.get(id=request.get('userId')),
            createDate=request.get('date'),
            img_url=request.get('imgUrl'),
            title=request.get('title'),
            content=request.get('content')
        )

        return ApiResponse.on_success(
            result=DiaryResultResponse(newDiary).data,
            response_status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기 삭제",
        operation_description="일기 삭제",
        responses={status.HTTP_200_OK: ApiResponse.schema(DiaryResultResponse, description='삭제 완료')}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryRequest)
    def delete(self, request, diaryId: int):
        findDiary = Diary.objects.get(id=diaryId)

        findDiary.delete()

        return ApiResponse.on_success(
            message="삭제 완료",
            response_status=status.HTTP_200_OK
        )


class DiaryCreateView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기 작성",
        operation_description="일기 작성",
        request_body=DiaryCreateRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(DiaryResultResponse)}
    )
    @validator(request_type=REQUEST_BODY, request_serializer=DiaryCreateRequest)
    def post(self, request):
        newDiary = Diary.create(
            user=User.objects.get(id=request.serializer.validated_data.get('userId')),
            createDate=request.serializer.validated_data.get('date'),
            title=request.serializer.validated_data.get('title'),
            content=request.serializer.validated_data.get('content')
        )

        return ApiResponse.on_success(
            result=DiaryResultResponse(newDiary).data,
            response_status=status.HTTP_201_CREATED
        )


class GetDiaryByUserView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="특정 유저의 일기 검색",
        operation_description="유저의 일기 조회",
        query_serializer=GetDiaryByDateRequest(),
        responses={status.HTTP_200_OK: ApiResponse.schema(DiaryResultResponse, many=True)}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetUserRequest, return_key='serializer')
    @validator(request_type=REQUEST_QUERY, request_serializer=GetDiaryByDateRequest, return_key='query')
    def get(self, request, userId: int):
        # User 가져오기
        findUser = User.objects.get(id=userId)

        # User와 연관된 모든 Diary 가져오기
        if 'date' in request.query.validated_data:
            findDiaries = Diary.objects.filter(user=findUser, createDate=request.query.validated_data['date'])
        else:
            findDiaries = Diary.objects.filter(user=findUser)

        return ApiResponse.on_success(
            result=DiaryResultResponse(findDiaries, many=True).data,
            response_status=status.HTTP_200_OK
        )


class GetQuizView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기회상 퀴즈",
        operation_description="일기회상 퀴즈",
        query_serializer=GetDiaryRequest(),
        # responses={status.HTTP_200_OK: ApiResponse.schema(QuizResultResponse, description="퀴즈")}
    )
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
    @swagger_auto_schema(
        operation_id="일기회상 답안 확인",
        operation_description="일기회상 답안 확인",
        request_body=AnswerListRequest,
        # responses={status.HTTP_200_OK: ApiResponse.schema(AnswerResultResponse, description="결과")}
    )
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


class GetNodeData(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="그래프 데이터 가져오기",
        operation_description="노드데이터 가져오기",
        responses={status.HTTP_200_OK: ApiResponse.schema(GraphDataSerializer)}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryRequest)
    def get(self, request, diaryId):
        findDiary = Diary.objects.get(id=diaryId)
        # 그래프 데이터 가져오기
        conn = GraphDB()
        result = conn.find_all_by_user_diary(findDiary.user.id, diaryId)

        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_200_OK
        )


class DiaryImgSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기 이미지 저장",
        operation_description="일기 이미지 저장",
        request_body=ImageUrlRequest,
        responses={status.HTTP_201_CREATED: ApiResponse.schema(DiaryResultResponse, description='저장 성공')}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryRequest, return_key='dump')
    @validator(request_type=REQUEST_BODY, request_serializer=ImageUrlRequest, return_key='serializer')
    def post(self, request, diaryId: int):
        # keyword 객체 가져오기
        diary = Diary.objects.get(id=diaryId)

        # imgUrl 저장
        diary.imgUrl = request.serializer.validated_data.get('imgUrl')
        diary.save()

        return ApiResponse.on_success(
            result=DiaryResultResponse(diary).data,
            response_status=status.HTTP_201_CREATED
        )
