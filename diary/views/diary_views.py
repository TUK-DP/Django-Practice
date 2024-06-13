import calendar

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView
from rest_framework import status

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_BODY, REQUEST_PATH, REQUEST_QUERY
from diary.serialziers.diary_serializers import *
from diary.serialziers.graph_serializers import GraphDataSerializer
from diary.serialziers.image_serializers import ImageUrlRequest
from diary.serialziers.keyword_serializers import KeywordResultSerializer
from users.models import User
from diary.utils.graph.graph import GraphDB


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
        diary_dict = {day: {"isExist": False, "diaryId": None} for day in range(1, lastDay + 1)}

        # 해당 userId, year, month에 해당하는 일기를 조회
        diaries = Diary.objects.filter(user_id=userId, createDate__year=year, createDate__month=month)

        # 조회된 일기의 날짜를 boolean 배열에 반영
        for diary in diaries:
            diary_dict[diary.createDate.day]["isExist"] = True
            diary_dict[diary.createDate.day]["diaryId"] = diary.id

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

        # 유저 정보를 UserSafeSerializer를 사용해서 구조화
        user_info = UserSafeSerializer(user).data
        # 일기 정보를 DiaryResultResponse를 사용하여 직렬화
        diary_list = DiaryResultResponse(diaries, many=True).data

        result = GetDiaryByUserAndDateResponse.to_json(user_data=user_info, diaries_data=diary_list)

        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_200_OK
        )
