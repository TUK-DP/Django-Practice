from diary.validator import *


class ImageUrlRequest(serializers.Serializer):
    imgUrl = serializers.CharField()
