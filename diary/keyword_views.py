from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_BODY, REQUEST_PATH
from diary.serializers import *


class GetKeywordView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기별 키워드 조회",
        operation_description="일기별 키워드 조회",
        response={status.HTTP_200_OK: ApiResponse.schema(KeywordResultSerializer, many=True)}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryRequest)
    def get(self, request, diaryId: int):
        # Diary 가져오기
        diary = Diary.objects.get(id=diaryId)

        # Diary 연관된 모든 Keyword 가져오기
        findKeywords = Keywords.objects.filter(diary=diary)

        return ApiResponse.on_success(
            result=KeywordResultSerializer(findKeywords, many=True).data,
            response_status=status.HTTP_200_OK
        )


class KeywordImgSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="키워드별 이미지 저장",
        operation_description="키워드별 이미지 저장",
        request_body=ImageUrlRequest,
        responses={status.HTTP_201_CREATED: ApiResponse.schema(KeywordSerializer, description='저장 성공')}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryRequest, return_key='dump')
    @validator(request_type=REQUEST_BODY, request_serializer=ImageUrlRequest, return_key='serializer')
    def post(self, request, keywordId: int):
        request: ReturnDict = request.serializer.validated_data

        # keyword 객체 가져오기
        keyword = Keywords.objects.get(id=keywordId)

        # imgUrl 저장
        keyword.imgUrl = request.get('imgUrl')
        keyword.save()

        return ApiResponse.on_success(
            result=KeywordSerializer(keyword).data,
            response_status=status.HTTP_201_CREATED
        )
