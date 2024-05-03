from rest_framework import serializers
from rest_framework import status

from config.paging_handler import PagingSerializer, get_paging_data


class ImageRequest(serializers.Serializer):
    image = serializers.ImageField()

    def is_valid(self, *, raise_exception=False):
        super_valid = super().is_valid()
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        return True, status.HTTP_200_OK


class ImageResponse(serializers.Serializer):
    imageUrl = serializers.CharField()


class KeywordImagePaging(PagingSerializer):
    imgUrls = serializers.ListField(child=serializers.CharField())

    def __init__(self, *args, page=1, pageSize=1, object_list=None, **kwargs):
        if object_list is None:
            object_list = []

        data = get_paging_data(page, pageSize, object_list, data_name="imgUrls")

        super().__init__(data, *args, **kwargs)
