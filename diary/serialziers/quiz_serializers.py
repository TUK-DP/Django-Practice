from diary.models import Questions
from diary.validator import *


class QuestionSerializer(serializers.Serializer):
    questionId = serializers.IntegerField()
    question = serializers.CharField()
    keywordId = serializers.IntegerField()

    @staticmethod
    def to_json(question: Questions):
        return {
            'questionId': question.id,
            'question': question.question,
            'keywordId': question.keyword.id
        }


class AnswerSerializer(serializers.Serializer):
    keywordId = serializers.IntegerField(validators=[exist_keyword_id])
    answer = serializers.CharField(allow_blank=True)


class AnswerListRequest(serializers.Serializer):
    answers = AnswerSerializer(many=True)
