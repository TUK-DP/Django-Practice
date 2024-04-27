from rest_framework import serializers, status

from .models import DiagRecord
from .token_serializer import TokenSerializer
from .validator import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'nickname', 'birth', 'isDeleted', 'created_at', 'updated_at']


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'birth', 'created_at', 'updated_at']


class DiagRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagRecord
        fields = ['id', 'user', 'totalQuestionSize', 'yesCount', 'created_at', 'updated_at']


class UserIdReqeust(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])


class UserCreateRequest(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    nickname = serializers.CharField(max_length=20, validators=[not_exist_user_nickname])
    email = serializers.EmailField(max_length=100, validators=[not_exist_user_email])
    password = serializers.CharField(max_length=128)
    birth = serializers.DateField()

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class LoginRequest(serializers.Serializer):
    email = serializers.CharField(max_length=20, validators=[exist_user_email])
    password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        validate_login(attrs['email'], attrs['password'])
        return attrs


class LoginResponse(serializers.Serializer):
    user = UserSerializer()
    token = TokenSerializer()


class DuplicateNicknameRequest(serializers.Serializer):
    nickname = serializers.CharField(max_length=20, validators=[not_exist_user_nickname])


class UserDeleteRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user_id])


class UserUpdateRequest(serializers.Serializer):
    username = serializers.CharField(max_length=20, required=False)
    nickname = serializers.CharField(max_length=20, validators=[not_exist_user_nickname], required=False)
    email = serializers.EmailField(max_length=100, validators=[not_exist_user_email], required=False)
    password = serializers.CharField(max_length=128, required=False)
    birth = serializers.DateField(required=False)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.birth = validated_data.get('birth', instance.birth)
        instance.save()
        return instance


class RecordSaveRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    totalQuestionSize = serializers.IntegerField()
    yesCount = serializers.IntegerField()
