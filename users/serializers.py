from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'nickname', 'birth', 'created_at', 'updated_at']


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'birth', 'created_at', 'updated_at']

class UserCreateRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'birth']

    def to_user(self) -> UserSerializer:
        newUser = UserSerializer(data=self.data)
        newUser.is_valid()
        newUser.save()
        return newUser


class LoginRequest(serializers.Serializer):
    nickname = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128)


class DeleteRequest(serializers.Serializer):
    nickname = serializers.CharField(max_length=20)


class UpdateResquest(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=20)
    nickname = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=128)
    birth = serializers.DateField()


class UserResponse(serializers.Serializer):
    isSuccess = serializers.BooleanField()
    result = UserSerializer(source='*')
