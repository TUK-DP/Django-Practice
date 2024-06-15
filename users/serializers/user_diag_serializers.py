from rest_framework import serializers

from users.models import DiagRecord
from users.validator import *


class DiagRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.IntegerField()
    totalQuestionSize = serializers.IntegerField()
    yesCount = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    @staticmethod
    def to_json(diag_record: DiagRecord):
        return DiagRecordSerializer.to_validated_serializer(diag_record).data

    @staticmethod
    def to_validated_serializer(diag_record: DiagRecord):
        serializer = DiagRecordSerializer(data={
            'id': diag_record.id,
            'user': diag_record.user.id,
            'totalQuestionSize': diag_record.totalQuestionSize,
            'yesCount': diag_record.yesCount,
            'created_at': diag_record.created_at,
            'updated_at': diag_record.updated_at
        })

        serializer.is_valid(raise_exception=True)

        return serializer


class RecordSaveRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    totalQuestionSize = serializers.IntegerField()
    yesCount = serializers.IntegerField()
