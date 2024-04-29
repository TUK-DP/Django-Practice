import os
import uuid
from datetime import datetime

from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from config.basemodel import ApiResponse
from image.s3_modules.s3_handler import upload_file_to_s3
from image.serializer import ImageRequest


# Create your views here.

class ImageView(APIView):
    parser_classes = [MultiPartParser]

    @transaction.atomic
    @swagger_auto_schema(
        operation_id="이미지 업로드",
        operation_description="이미지 업로드",
        manual_parameters=[
            # image
            openapi.Parameter(
                name='image',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='이미지 파일'
            ),
            #
        ],
        responses={
            status.HTTP_200_OK: '업로드 성공'
        },
    )
    def post(self, request):
        requestSerial = ImageRequest(data=request.data)
        isValid, response_status = requestSerial.is_valid(raise_exception=True)

        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(
                requestSerial.errors, response_status=response_status
            )

        # 파일 이름 자르기 [0]은 파일 이름, [1]은 확장자
        splitext = os.path.splitext(request.data.get('image').name)

        # uuid 생성
        uuid_str = str(uuid.uuid4())

        # 파일확장자
        file_extension = splitext[1]

        # 파일이름 = 현재시간 + uuid + 확장자
        filename = (datetime.now().strftime("%d-%m-%YT%H:%M:%S") + uuid_str + file_extension)

        # S3에 이미지 업로드
        url = upload_file_to_s3(request.data.get('image'), filename)
        return ApiResponse.on_success(
            result={
                'imageUrl': url
            },
            response_status=status.HTTP_200_OK
        )
