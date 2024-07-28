from rest_framework import serializers

from config.utils import transfer_dict_key_to_camel_case

from diag.models import DiagRecord
from users.validator import *
from users.serializers.user_get_post_put_delete_serializers import UserSafeSerializer


class DiagRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = UserSafeSerializer(read_only=True)
    total_question_size = serializers.IntegerField()
    total_score = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        camel_case_representation = transfer_dict_key_to_camel_case(representation)
        return camel_case_representation


class RecordSaveRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    totalQuestionSize = serializers.IntegerField()
    diagAnswer = serializers.ListField(child=serializers.IntegerField())


class QuestionResponse(serializers.Serializer):
    question = serializers.CharField(max_length=255)