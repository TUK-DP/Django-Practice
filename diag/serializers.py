from rest_framework import serializers

from config.utils import transfer_dict_key_to_camel_case

from diag.models import DiagRecord
from users.validator import *


class DiagRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.IntegerField()
    total_question_size = serializers.IntegerField()
    yes_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        camel_case_representation = transfer_dict_key_to_camel_case(representation)
        return camel_case_representation

    # @staticmethod
    # def to_json(diag_record: DiagRecord):
    #     return DiagRecordSerializer.to_validated_serializer(diag_record).data

    # @staticmethod
    # def to_validated_serializer(diag_record: DiagRecord):
    #     serializer = DiagRecordSerializer(data={
    #         'id': diag_record.id,
    #         'user': diag_record.user.id,
    #         'totalQuestionSize': diag_record.totalQuestionSize,
    #         'yesCount': diag_record.yesCount,
    #         'created_at': diag_record.created_at,
    #         'updated_at': diag_record.updated_at
    #     })

    #     serializer.is_valid(raise_exception=True)

    #     return serializer


class RecordSaveRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    totalQuestionSize = serializers.IntegerField()
    yesCount = serializers.IntegerField()
