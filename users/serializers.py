from rest_framework import serializers, status

from .validator import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'nickname', 'birth', 'created_at', 'updated_at']


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'birth', 'created_at', 'updated_at']


class UserCreateRequest(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    nickname = serializers.CharField(max_length=20, validators=[not_exist_nickname])
    email = serializers.EmailField(max_length=100, validators=[not_exist_email])
    password = serializers.CharField(max_length=128)
    birth = serializers.DateField()

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class LoginRequest(serializers.Serializer):
    email = serializers.CharField(max_length=20, validators=[exist_email])
    password = serializers.CharField(max_length=128)

    def is_valid(self, *, raise_exception=False):
        super_valid = super().is_valid()
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        if not (User.objects.filter(
                email=self.validated_data.get('email'),
                password=self.validated_data.get('password'))
                .exists()):
            self._errors['error'] = '존재하지 않는 사용자입니다.'
            return False, status.HTTP_400_BAD_REQUEST

        return True, status.HTTP_200_OK


class DuplicateNicknameRequest(serializers.Serializer):
    nickname = serializers.CharField(max_length=20, validators=[not_exist_nickname])


class UserDeleteRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user])


class UserUpdateRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user])
    username = serializers.CharField(max_length=20, required=False)
    nickname = serializers.CharField(max_length=20, validators=[not_exist_nickname], required=False)
    email = serializers.EmailField(max_length=100, validators=[not_exist_email], required=False)
    password = serializers.CharField(max_length=128, required=False)
    birth = serializers.DateField()
