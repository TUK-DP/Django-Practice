import calendar

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_PATH, REQUEST_QUERY
from diary.serialziers.diary_response_serializers import *
from diary.serialziers.diray_request_serializers import *
from users.models import User


class GetDiaryByUserView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="특정 유저의 일기 검색 (with Date)",
        operation_description="유저의 일기 조회",
        query_serializer=GetDiaryByDateRequest(),
        responses={status.HTTP_200_OK: ApiResponse.schema(DiaryResultResponse, many=True)}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=UserIdReqeust, return_key='serializer')
    @validator(request_type=REQUEST_QUERY, request_serializer=GetDiaryByDateRequest, return_key='query')
    def get(self, request, userId: int):
        # User 가져오기
        findUser = User.objects.get(id=userId)

        # User와 연관된 모든 Diary 가져오기
        if 'date' in request.query.validated_data:
            findDiaries = Diary.objects.filter(user=findUser, createDate=request.query.validated_data['date'])
        else:
            findDiaries = Diary.objects.filter(user=findUser)

        # 직렬화
        return ApiResponse.on_success(
            result=[GetDiaryDetailResponse.to_json(diary=diary) for diary in findDiaries],
            response_status=status.HTTP_200_OK
        )


class CheckDiaryEntriesView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="기간별 일기 유무 리스트 가져오기",
        operation_description="기간별 일기 유무 리스트 가져오기",
        query_serializer=CheckDiaryEntriesRequest(),
        responses={status.HTTP_200_OK: ApiResponse.schema(ApiResponse)}
    )
    @validator(request_type=REQUEST_QUERY, request_serializer=CheckDiaryEntriesRequest, return_key='query')
    def get(self, request):
        # 요청 데이터에서 userId, year, month 추출
        userId = request.query.validated_data.get('userId')
        year = request.query.validated_data.get('year')
        month = request.query.validated_data.get('month')

        # 해당 월의 일수를 가져옴
        _, lastDay = calendar.monthrange(year, month)

        # 일기가 존재하는 날짜를 dict으로 초기화
        diary_dict = {day: {"isExist": False, "diaryId": None, "imgExist": False} for day in range(1, lastDay + 1)}

        # 해당 userId, year, month에 해당하는 일기를 조회
        diaries = Diary.objects.filter(user_id=userId, createDate__year=year, createDate__month=month)

        # 조회된 일기의 날짜를 boolean 배열에 반영
        for diary in diaries:
            diary_dict[diary.createDate.day]["isExist"] = True
            diary_dict[diary.createDate.day]["diaryId"] = diary.id

            img_exist = False

            # diary와 연결된 keyword들에서 imgUrl이 None이 아닌 경우 확인
            if any(keyword.imgUrl is not None for keyword in diary.keywords.all()):
                img_exist = True

            # diary 자체에 imgUrl이 존재하는 경우 확인
            if diary.imgUrl is not None:
                img_exist = True

            diary_dict[diary.createDate.day]["imgExist"] = img_exist

        # 결과를 JSON 형식으로 반환
        result = {f'{year}-{month}': diary_dict}
        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_200_OK
        )


class GetDiaryByUserAndDateView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="기간별 일기 리스트 가져오기",
        operation_description="기간별 일기 리스트 가져오기",
        query_serializer=GetDiaryByUserAndDateRequest(),
        responses={status.HTTP_200_OK: ApiResponse.schema(ApiResponse)}
    )
    @validator(request_type=REQUEST_QUERY, request_serializer=GetDiaryByUserAndDateRequest, return_key='query')
    def get(self, request):
        # 요청 데이터에서 userId, year, month 추출
        userId = request.query.validated_data.get('userId')
        startDate = request.query.validated_data.get('startDate')
        finishDate = request.query.validated_data.get('finishDate')
        sortBy = request.query.validated_data.get('sortBy')

        sortField = DATE_SORT_MAPPER.get(sortBy)

        # 해당 userId, startDate, finishDate에 해당하는 일기를 조회
        diaries = Diary.objects.filter(
            user_id=userId,
            createDate__range=[startDate, finishDate]
        ).order_by(sortField)

        # 해당 userId를 가지고 있는 유저 정보 가져오기
        user = User.objects.get(id=userId)

        return ApiResponse.on_success(
            result=GetDiariesByUserAndDateResponse.to_json(user=user, diaries=diaries),
            response_status=status.HTTP_200_OK
        )


class GetDiaryPagingView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="유저별 일기 페이징",
        operation_description="유저별 일기 페이징",
        query_serializer=GetDiaryPagingRequset(),
        responses={status.HTTP_200_OK: ApiResponse.schema(DiaryPagingResponse)}
    )
    @validator(request_type=REQUEST_QUERY, request_serializer=GetDiaryPagingRequset, return_serializer="serializer")
    def get(self, request):
        request = request.serializer.validated_data

        # 최신순으로 정렬
        diaryList = Diary.objects.filter(
            user=User.objects.get(id=request.get('userId'))
        ).order_by('-createDate')

        requestPage = request.get('page')
        pageSize = request.get('pageSize')

        result = DiaryPagingResponse(page=requestPage, pageSize=pageSize, object_list=diaryList)

        return ApiResponse.on_success(
            result=result.data,
            response_status=status.HTTP_200_OK
        )