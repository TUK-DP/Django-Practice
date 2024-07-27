from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from config.basemodel import validator
from config.settings import REQUEST_BODY, REQUEST_QUERY
from diag.serializers import *
from users.serializers.user_get_post_put_delete_serializers import UserIdReqeust


class RecordView(APIView):
    @transaction.atomic 
    @swagger_auto_schema(
        operation_id="치매진단 결과 저장",
        operation_description="유저의 치매진단 결과 저장", request_body=RecordSaveRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(DiagRecordSerializer)}
    )
    @validator(request_serializer=RecordSaveRequest, request_type=REQUEST_BODY, return_key="serializer")
    def post(self, request):
        request = request.serializer.validated_data

        # DiagRecord 객체 생성
        diag_record = DiagRecord.objects.create(
            total_question_size=request.get('totalQuestionSize'),
            yes_count=request.get('yesCount'),
            user=User.objects.get(id=request.get('userId'), is_deleted=False)
        )

        return ApiResponse.on_success(
            result=DiagRecordSerializer(diag_record),
            response_status=status.HTTP_200_OK
        )
    
    @transaction.atomic
    @swagger_auto_schema(
        operation_id="최근 진단 기록 조회",
        operation_description="유저의 이전 진단 기록 조회", query_serializer=UserIdReqeust,
        responses={status.HTTP_200_OK: ApiResponse.schema(DiagRecordSerializer)}
    )
    @validator(request_serializer=UserIdReqeust, request_type=REQUEST_QUERY, return_key='serializer')
    def get(self, request):
        request = request.serializer.validated_data

        diag_record = DiagRecord.objects.filter(
            user=User.objects.get(id=request.get('userId'))
        ).order_by('-created_at').first()

        return ApiResponse.on_success(
            result=DiagRecordSerializer(diag_record),
            response_status=status.HTTP_200_OK
        )