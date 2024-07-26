from rest_framework import serializers

from users.validator import *
from config.utils import transfer_camel_case


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        camel_case_representation = transfer_camel_case(representation)
        return camel_case_representation


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'account_id', 'username', 'created_at', 'updated_at']


class UserIdReqeust(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])


class UserCreateRequest(serializers.Serializer):
    accountId = serializers.CharField(max_length=128, validators=[not_exist_user_account_id])
    password = serializers.CharField(max_length=128)
    username = serializers.CharField(max_length=20)

    def create(self, validated_data):
        user_data = {
            'account_id': validated_data['accountId'],
            'password': validated_data['password'],
            'username': validated_data['username'],
        }
        return User.objects.create(**user_data)


class UserUpdateRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user_id])
    accountId = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)
    username = serializers.CharField(max_length=20)

    def validate(self, attrs):
        validate_update(attrs['id'], attrs['accountId'])
        return attrs

    def update(self, instance, validated_data):
        instance.account_id = validated_data.get('accountId', instance.account_id)
        instance.password = validated_data.get('password', instance.password)
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        return instance


class UserDeleteRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user_id])