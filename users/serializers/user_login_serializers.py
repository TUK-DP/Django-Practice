from rest_framework import serializers

from users.serializers.user_get_post_put_delete_serializers import UserSerializer
from users.token_serializer import TokenSerializer
from users.validator import *


class LoginRequest(serializers.Serializer):
    accountId = serializers.CharField(max_length=100, validators=[exist_user_account_id])
    password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        validate_login(attrs['accountId'], attrs['password'])
        return attrs


class LoginResponse(serializers.Serializer):
    user = UserSerializer()
    token = TokenSerializer()
