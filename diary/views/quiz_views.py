from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_BODY, REQUEST_QUERY
from diary.serialziers.diray_request_serializers import *
from diary.serialziers.quiz_serializers import AnswerListRequest, QuestionSerializer


class GetQuizView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기회상 퀴즈",
        operation_description="일기회상 퀴즈",
        query_serializer=GetDiaryByIdRequest(),
        # responses={status.HTTP_200_OK: ApiResponse.schema(QuizResultResponse, description="퀴즈")}
    )
    @validator(request_type=REQUEST_QUERY, request_serializer=GetDiaryByIdRequest, return_key='query')
    def get(self, request):
        # Diary 가져오기
        findDiary = Diary.objects.get(id=request.query.validated_data.get('diaryId'))

        keywords = findDiary.keywords.all()

        # 모든 Sentence 와 연관된 Question 가져오기
        result = []
        for keyword in keywords:
            question = keyword.questions.first()
            result.append(QuestionSerializer.to_json(question))

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
    @validator(request_type=REQUEST_BODY, request_serializer=AnswerListRequest)
    def post(self, request):
        requestSerial = request.serializer
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
