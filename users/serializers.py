from rest_framework import serializers, status

from .models import User, DiagRecord
from .token_serializer import TokenSerializer
from .validator import *


class UserIdRequire(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])


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


# class LoginRequest(serializers.Serializer):
#     nickname = serializers.CharField(max_length=20)
#     password = serializers.CharField(max_length=128)
#
#     def is_valid(self, raise_exception=False):
#         super_valid = super().is_valid()
#         # 유효하지 않다면 False, 400 반환
#         if not super_valid:
#             return False, status.HTTP_400_BAD_REQUEST
#
#         # 유효하다면 nickname이 존재하는지 확인
#         is_user_exist = User.objects.filter(nickname=self.data['nickname'], isDeleted='False').exists()
#
#         # 존재하지 않는다면 False, 404 반환
#         if not is_user_exist:
#             self._errors['nickname'] = [f'nickname: {self.data.get("nickname")} 가 존재하지 않습니다.']
#             return False, status.HTTP_404_NOT_FOUND
#
#         return True, status.HTTP_200_OK


# class UserIdReqeust(serializers.Serializer):
#     userId = serializers.IntegerField()
#
#     def is_valid(self, raise_exception=False):
#         super_valid = super().is_valid()
#         # 유효하지 않다면 False, 400 반환
#         if not super_valid:
#             return False, status.HTTP_400_BAD_REQUEST
#
#         # 유효하다면 userId가 존재하는지 확인
#         is_user_exist = User.objects.filter(id=self.data['userId'], isDeleted='False').exists()
#
#         # 존재하지 않는다면 False, 404 반환
#         if not is_user_exist:
#             self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
#             return False, status.HTTP_404_NOT_FOUND
#
#         return True, status.HTTP_200_OK


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
    userId = serializers.IntegerField()
    totalQuestionSize = serializers.IntegerField()
    yesCount = serializers.IntegerField()

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # 유효하다면 userId가 존재하는지 확인
        is_user_exists = User.objects.filter(id=self.data['userId'], isDeleted='False').exists()

        # 존재하지 않는다면 False, 404 반환
        if not is_user_exists:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK