from diary.models import Questions
from diary.serialziers.keyword_serializers import KeywordSerializer
from diary.validator import *


class QuestionSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(read_only=True)

    class Meta:
        model = Questions
        fields = '__all__'


class AnswerSerializer(serializers.Serializer):
    keywordId = serializers.IntegerField(validators=[exist_keyword_id])
    answer = serializers.CharField(allow_blank=True)


class AnswerListRequest(serializers.Serializer):
    answers = AnswerSerializer(many=True)
