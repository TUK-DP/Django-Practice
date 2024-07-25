from rest_framework import serializers

from users.validator import *
import inflection


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 필드 이름을 CamelCase로 변경
        camel_case_representation = {
            inflection.camelize(key, False): value for key, value in representation.items()
        }
        return camel_case_representation

    @property
    def transfer_camel_case(self):
        return self.data


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'account_id', 'user_name', 'created_at', 'updated_at']


class UserIdReqeust(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])


class UserCreateRequest(serializers.Serializer):
    accountId = serializers.CharField(max_length=128, validators=[not_exist_user_account_id])
    passWord = serializers.CharField(max_length=128)
    userName = serializers.CharField(max_length=20)

    def create(self, validated_data):
        user_data = {
            'account_id': validated_data['accountId'],
            'pass_word': validated_data['passWord'],
            'user_name': validated_data['userName'],
        }
        return User.objects.create(**user_data)


class UserUpdateRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user_id])
    accountId = serializers.CharField(max_length=128)
    passWord = serializers.CharField(max_length=128)
    userName = serializers.CharField(max_length=20)

    def validate(self, attrs):
        validate_update(attrs['id'], attrs['accountId'])
        return attrs

    def update(self, instance, validated_data):
        instance.account_id = validated_data.get('accountId', instance.account_id)
        instance.password = validated_data.get('passWord', instance.pass_word)
        instance.user_name = validated_data.get('userName', instance.user_name)
        instance.save()
        return instance


class UserDeleteRequest(serializers.Serializer):
    id = serializers.IntegerField(validators=[exist_user_id])