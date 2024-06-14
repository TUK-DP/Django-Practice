from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from config.settings import REQUEST_BODY, REQUEST_QUERY
from users.serializers import *


class RecordSaveView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="치매진단 결과 저장", request_body=RecordSaveRequest,
                         responses={200: '닉네임 사용 가능'})
    @validator(request_serializer=RecordSaveRequest, request_type=REQUEST_BODY, return_key="serializer")
    def post(self, request):
        request = request.serializer.validated_data

        # DiagRecord 객체 생성
        diagRecord = DiagRecord.objects.create(
            totalQuestionSize=request.get('totalQuestionSize'),
            yesCount=request.get('yesCount'),
            user=User.objects.get(id=request.get('userId'), isDeleted='False')
        )

        return ApiResponse.on_success(
            result=DiagRecordSerializer(diagRecord).data,
            response_status=status.HTTP_200_OK
        )


class GetDiagRecordView(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="유저의 이전 진단 기록 조회", query_serializer=UserIdReqeust,
                         response={"200": DiagRecordSerializer})
    @validator(request_serializer=UserIdReqeust, request_type=REQUEST_QUERY, return_key='serializer')
    def get(self, request):
        request = request.serializer.validated_data

        diagRecord = DiagRecord.objects.filter(
            user=User.objects.get(id=request.get('userId'))).order_by('-created_at').first()

        return ApiResponse.on_success(
            result=DiagRecordSerializer(diagRecord).data,
            response_status=status.HTTP_200_OK
        )
