from rest_framework import serializers

from config.paging_handler import PagingSerializer, get_paging_data
from image.validator import less_than


class ImageUrlRequest(serializers.Serializer):
    imgUrl = serializers.CharField()


class ImageFileRequest(serializers.Serializer):
    image = serializers.ImageField()


class ImageUploadResponse(serializers.Serializer):
    imageUrl = serializers.CharField()

    @staticmethod
    def to_json(url: str):
        return {
            'imageUrl': url
        }


class KeywordImagePaging(PagingSerializer):
    imgUrls = serializers.ListField(child=serializers.CharField())

    def __init__(self, *args, page=1, pageSize=1, object_list=None, **kwargs):
        if object_list is None:
            object_list = []

        data = get_paging_data(page, pageSize, object_list, data_name="imgUrls")

        super().__init__(data, *args, **kwargs)


class GenerateImageRequest(serializers.Serializer):
    password = serializers.CharField()
    prompt = serializers.CharField()
    n = serializers.IntegerField(validators=[less_than(4)])


class GenerateImageStatusRequest(serializers.Serializer):
    password = serializers.CharField()
    taskId = serializers.CharField()


class GenerateImageResponse(serializers.Serializer):
    urls = serializers.ListField(child=serializers.CharField())

    
class GenerateImageStatusResponse(serializers.Serializer):
    state = serializers.CharField()
    status = serializers.CharField()
    result = serializers.ListField(child=serializers.URLField(), required=False)
    error = serializers.CharField(required=False)