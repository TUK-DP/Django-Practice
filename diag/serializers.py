from rest_framework import serializers

from config.utils import transfer_dict_key_to_camel_case

from diag.models import DiagRecord
from diag.questions import QUESTION_LIST
from users.validator import *
from users.serializers.user_get_post_put_delete_serializers import UserSafeSerializer


class DiagRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagRecord
        fields = ['id', 'total_score']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        camel_case_representation = transfer_dict_key_to_camel_case(representation)
        return camel_case_representation


class RecordSaveRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    diagAnswer = serializers.ListField(child=serializers.IntegerField())

    def validate(self, data):
        diag_answer = data.get('diagAnswer')

        if len(QUESTION_LIST) != len(diag_answer):
            raise ValidationError("답안의 길이와 질문의 길이가 일치하지 않습니다.")

        return data


class QuestionResponse(serializers.Serializer):
    question = serializers.CharField(max_length=255)