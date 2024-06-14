from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_BODY, REQUEST_PATH
from diary.serialziers.diray_request_serializers import *
from diary.serialziers.keyword_serializers import *
from image.serializers import ImageUrlRequest


class GetKeywordView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="일기별 키워드 조회",
        operation_description="일기별 키워드 조회",
        response={status.HTTP_200_OK: ApiResponse.schema(KeywordResponse, many=True)}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryByIdRequest)
    def get(self, request, diaryId: int):
        # Diary 가져오기
        diary = Diary.objects.get(id=diaryId)

        # Diary 연관된 모든 Keyword 가져오기
        findKeywords = Keywords.objects.filter(diary=diary)

        return ApiResponse.on_success(
            result=KeywordResponse(findKeywords, many=True).data,
            response_status=status.HTTP_200_OK
        )


class KeywordImgSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="키워드별 이미지 저장",
        operation_description="키워드별 이미지 저장",
        request_body=ImageUrlRequest,
        responses={status.HTTP_201_CREATED: ApiResponse.schema(KeywordResponse, description='저장 성공')}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=KeywordIdRequest, request_body='dump')
    @validator(request_type=REQUEST_BODY, request_serializer=ImageUrlRequest, return_key='image_url_request')
    def post(self, request, keywordId: int):
        # keyword 객체 가져오기
        keyword = Keywords.objects.get(id=keywordId)

        # imgUrl 저장
        keyword.imgUrl = request.image_url_request.validated_data.get('imgUrl')
        keyword.save()

        return ApiResponse.on_success(
            result=KeywordResponse.to_json(keyword),
            response_status=status.HTTP_201_CREATED
        )
