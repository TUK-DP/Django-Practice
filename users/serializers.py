from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'created_at', 'updated_at']


class UserCreateRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def to_user(self) -> UserSerializer:
        newUser = UserSerializer(data=self.data)
        newUser.is_valid()
        newUser.save()
        return newUser


class LoginRequest(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128)


class DeleteRequest(serializers.Serializer):
    username = serializers.CharField(max_length=20)


class UpdateResquest(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=128)


class UserResponse(serializers.Serializer):
    isSuccess = serializers.BooleanField()
    result = UserSerializer(source='*')