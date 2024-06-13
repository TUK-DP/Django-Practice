from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_BODY, REQUEST_PATH
from diary.serialziers.diary_serializers import *
from diary.serialziers.image_serializers import ImageUrlRequest
from users.models import User


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

        # 일기 삭제 후 재생성
        newDiary = requestSerializer.update(findDiary, request)

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
        Diary.objects.filter(id=diaryId).delete()

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
