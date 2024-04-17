from rest_framework import serializers, status

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

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # 유효하다면 nickname이 존재하는지 확인
        is_user_exist = User.objects.filter(nickname=self.data['nickname']).exists()

        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK 


class NicknameRequest(serializers.Serializer):
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
