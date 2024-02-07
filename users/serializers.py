from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'created_at', 'updated_at')


class UserCreateRequest(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def to_user(self) -> UserSerializer:
        newUser = UserSerializer(data=self.data)
        newUser.is_valid()
        newUser.save()
        return newUser
