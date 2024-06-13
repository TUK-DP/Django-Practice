from rest_framework import status

from config.validator import positive_value
from config.sort_options import *
from diary.serialziers.diary_serializers import DiarySerializer
from users.models import User
from users.serializers import UserSafeSerializer
from users.validator import exist_user_id
from diary.models import Questions
from diary.validator import *


class KeywordSerializer(serializers.ModelSerializer):
    sentence = DiarySerializer(read_only=True)

    class Meta:
        model = Keywords
        fields = '__all__'


class KeywordResultSerializer(serializers.ModelSerializer):
    keywordId = serializers.IntegerField(source="id")

    class Meta:
        model = Keywords
        fields = ['keywordId', 'keyword', 'imgUrl']


class KeywordIdRequest(serializers.Serializer):
    keywordId = serializers.IntegerField(validators=[exist_keyword_id])


class FindKeywordImgRequest(serializers.Serializer):
    keyword = serializers.CharField()
    page = serializers.IntegerField(validators=[positive_value])
    pageSize = serializers.IntegerField(validators=[positive_value])
