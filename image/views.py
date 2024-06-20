from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from config.basemodel import ApiResponse, validator
from config.settings import REQUEST_QUERY, JWT_SECRET, REQUEST_BODY
from diary.serialziers.keyword_serializers import *
from image.gpt.GenerateImage import generate_upload_image, test_generate_image_urls
from image.s3_modules.s3_handler import upload_file_random_name_to_s3
from image.serializers import *


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

        # S3에 이미지 업로드
        url = upload_file_random_name_to_s3(image_file)

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


class GenerateImageView(APIView):
    @swagger_auto_schema(
        operation_id="AI 이미지 생성",
        operation_description="AI 이미지 생성",
        request_body=GenerateImageRequest,
        responses={status.HTTP_200_OK: ApiResponse.schema(GenerateImageResponse)}
    )
    @validator(request_type=REQUEST_BODY, request_serializer=GenerateImageRequest)
    def post(self, request):
        n = request.serializer.validated_data.get('n')
        prompt = request.serializer.validated_data.get('prompt')
        password = request.serializer.validated_data.get('password')

        try:
            if password != JWT_SECRET:
                urls = test_generate_image_urls(prompt, n=n)
            else:
                urls = generate_upload_image(prompt, n=n)
        except Exception as e:
            print(e)
            return ApiResponse.on_fail(message=str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return ApiResponse.on_success(result={'urls': urls}, response_status=status.HTTP_200_OK)
