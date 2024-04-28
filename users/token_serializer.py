from rest_framework import serializers

from users.validator import exist_user_id


class TokenSerializer(serializers.Serializer):
    AccessToken = serializers.CharField(validators=[])
    RefreshToken = serializers.CharField(validators=[])


class AutoLoginRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
