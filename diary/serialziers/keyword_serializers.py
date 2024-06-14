from config.validator import positive_value
from diary.validator import *


class KeywordResponse(serializers.Serializer):
    keywordId = serializers.IntegerField(source="id")
    keyword = serializers.CharField()
    imgUrl = serializers.CharField()

    @staticmethod
    def to_json(keyword: Keywords):
        return {
            'keywordId': keyword.id,
            'keyword': keyword.keyword,
            'imgUrl': keyword.imgUrl
        }


class KeywordIdRequest(serializers.Serializer):
    keywordId = serializers.IntegerField(validators=[exist_keyword_id])


class FindKeywordImgRequest(serializers.Serializer):
    keyword = serializers.CharField()
    page = serializers.IntegerField(validators=[positive_value])
    pageSize = serializers.IntegerField(validators=[positive_value])
