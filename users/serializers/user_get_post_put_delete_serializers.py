from rest_framework import serializers

from users.validator import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'nickname', 'birth', 'isDeleted', 'created_at', 'updated_at']


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nickname', 'birth', 'created_at', 'updated_at']


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


class UserUpdateRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user_id])
    username = serializers.CharField(max_length=20)
    nickname = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=128)
    birth = serializers.DateField()

    def validate(self, attrs):
        validate_update(attrs['id'], attrs['email'], attrs['nickname'])
        return attrs

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.birth = validated_data.get('birth', instance.birth)
        instance.save()
        return instance


class UserDeleteRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user_id])
