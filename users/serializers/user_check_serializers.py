from rest_framework import serializers

from users.validator import *


class DuplicateNicknameRequest(serializers.Serializer):
    nickname = serializers.CharField(max_length=100, validators=[not_exist_user_nickname])


class DuplicateEmailRequest(serializers.Serializer):
    email = serializers.CharField(max_length=100, validators=[not_exist_user_email])
