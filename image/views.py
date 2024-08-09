from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_QUERY, JWT_SECRET, REQUEST_BODY
from diary.serialziers.keyword_serializers import *

from image.s3_modules.s3_handler import upload_file_random_name_to_s3, bulk_upload_file_to_s3
from image.serializers import *

from tasks import *
from celery.result import AsyncResult

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
            status.HTTP_200_OK: ApiResponse.schema(ImageUploadResponse, description='이미지 업로드 성공')
        },
    )
    @validator(request_type=REQUEST_BODY, request_serializer=ImageFileRequest, return_serializer="serializer")
    def post(self, request):
        image_file = request.serializer.validated_data.get('image')

        try:
            # S3에 이미지 업로드
            url = upload_file_random_name_to_s3(image_file)
        except Exception as e:
            return ApiResponse.on_fail(
                message=str(e),
                response_status=status.HTTP_404_NOT_FOUND
            )


        return ApiResponse.on_success(
            result=ImageUploadResponse.to_json(url),
            response_status=status.HTTP_200_OK
        )

    @transaction.atomic
    @swagger_auto_schema(
        operation_id="키워드별 사진 페이징",
        operation_description="키워드별 사진 페이징",
        query_serializer=FindKeywordImgRequest(),
        responses={status.HTTP_200_OK: ApiResponse.schema(KeywordImagePaging)}
    )
    @validator(request_type=REQUEST_QUERY, request_serializer=FindKeywordImgRequest, return_serializer="serializer")
    def get(self, request):
        request = request.serializer.validated_data

        # 최신순으로 정렬
        keywords = Keywords.objects.filter(
            keyword=request.get('keyword'), imgUrl__isnull=False
        ).order_by('-updated_at')

        # imgUrl 필드만 가져와서 리스트로 변환하지 않고 쿼리셋으로 페이지네이션
        keywordImgUrls = keywords.values_list('imgUrl', flat=True)

        requestPage = request.get('page')
        pageSize = request.get('pageSize')

        result = KeywordImagePaging(page=requestPage, pageSize=pageSize, object_list=keywordImgUrls)

        return ApiResponse.on_success(
            result=result.data,
            response_status=status.HTTP_201_CREATED
        )


class ImageBulkUploadView(APIView):
    parser_classes = [MultiPartParser]

    @transaction.atomic
    @swagger_auto_schema(
        operation_id="여러 이미지 업로드",
        operation_description="여러 이미지 업로드",
        manual_parameters=[
            # image
            openapi.Parameter(
                name='images',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='이미지 파일들',
            ),
            #
        ],
        responses={
            status.HTTP_200_OK: ApiResponse.schema(ImageBulkUploadResponse, description='이미지 업로드 성공')
        },
    )
    @validator(request_type=REQUEST_BODY, request_serializer=ImageFilesReqeust, return_serializer="serializer")
    def post(self, request):
        image_files = request.serializer.validated_data.get('images')

        try:
            # S3에 이미지 업로드
            urls = bulk_upload_file_to_s3(image_files)
        except Exception as e:
            return ApiResponse.on_fail(
                message=str(e),
                response_status=status.HTTP_404_NOT_FOUND
            )


        return ApiResponse.on_success(
            result=ImageBulkUploadResponse.to_json(urls),
            response_status=status.HTTP_200_OK
        )


class GenerateImageView(APIView):
    @swagger_auto_schema(
        operation_id="AI 이미지 생성 요청",
        operation_description="AI 이미지 생성 요청",
        request_body=GenerateImageRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(GenerateImageResponse)}
    )
    @validator(request_type=REQUEST_BODY, request_serializer=GenerateImageRequest)
    def post(self, request):
        n = request.serializer.validated_data.get('n')
        prompt = request.serializer.validated_data.get('prompt')
        password = request.serializer.validated_data.get('password')

        if password != JWT_SECRET:
            task = test_generate_image.delay(prompt, n=n)
        else:
            task = generate_image.delay(prompt, n=n)

        return ApiResponse.on_success(result={'taskId': task.id}, response_status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_id="AI 이미지 생성 상태 확인",
        operation_description="AI 이미지 생성 상태 확인",
        query_serializer=GenerateImageStatusRequest(),
        responses={
            status.HTTP_200_OK: ApiResponse.schema(GenerateImageStatusResponse),
            status.HTTP_404_NOT_FOUND: "Task not found"
        }
    )
    @validator(request_type=REQUEST_QUERY, request_serializer=GenerateImageStatusRequest)
    def get(self, request):
        task_id = request.query_params.get('taskId')
        if not task_id: 
            return ApiResponse.on_error("Task ID is required", status.HTTP_400_BAD_REQUEST)

        task = AsyncResult(task_id) 

        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task is pending'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'status': 'Task is in progress' if task.state == 'PROCESSING' else 'Task completed',
                'result': task.result if task.state == 'SUCCESS' else None
            }
        else:
            response = {
                'state': task.state,
                'status': 'Task failed',
                'error': str(task.result)
            }
        
        return ApiResponse.on_success(result=GenerateImageStatusResponse(response).data, response_status=status.HTTP_200_OK)