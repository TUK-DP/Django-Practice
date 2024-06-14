from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_PATH
from diary.serialziers.diray_request_serializers import *
from diary.serialziers.graph_serializers import GraphDataSerializer
from diary.utils.graph.graph import GraphDB


class GetNodeData(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="그래프 데이터 가져오기",
        operation_description="노드데이터 가져오기",
        responses={status.HTTP_200_OK: ApiResponse.schema(GraphDataSerializer)}
    )
    @validator(request_type=REQUEST_PATH, request_serializer=GetDiaryByIdRequest)
    def get(self, request, diaryId):
        findDiary = Diary.objects.get(id=diaryId)
        # 그래프 데이터 가져오기
        conn = GraphDB()
        result = conn.find_all_by_user_diary(findDiary.user.id, diaryId)

        return ApiResponse.on_success(
            result=result,
            response_status=status.HTTP_200_OK
        )
