from rest_framework import serializers

from users.models import DiagRecord
from users.validator import *


class DiagRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagRecord
        fields = ['id', 'user', 'totalQuestionSize', 'yesCount', 'created_at', 'updated_at']


class RecordSaveRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    totalQuestionSize = serializers.IntegerField()
    yesCount = serializers.IntegerField()
