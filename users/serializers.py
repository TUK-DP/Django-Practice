from rest_framework import serializers, status

from .models import User, DiagRecord


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
        is_user_exist = User.objects.filter(nickname=self.data['nickname'], isDeleted='False').exists()

        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['nickname'] = [f'nickname: {self.data.get("nickname")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK 


class UserIdReqeust(serializers.Serializer):
    userId = serializers.IntegerField()

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # 유효하다면 userId가 존재하는지 확인
        is_user_exist = User.objects.filter(id=self.data['userId'], isDeleted='False').exists()

        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK


class NicknameRequest(serializers.Serializer):
    nickname = serializers.CharField(max_length=20)

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # 유효하다면 nickname이 존재하는지 확인
        is_user_exist = User.objects.filter(nickname=self.data['nickname'], isDeleted='False').exists()

        # 존재하지 않는다면 True, 200 반환
        if not is_user_exist:
            return True, status.HTTP_200_OK
        
        self._errors['nickname'] = [f'nickname: 이미 사용 중인 nickname입니다.']
        return False, status.HTTP_404_NOT_FOUND


class UpdateResquest(serializers.Serializer):
    userId = serializers.IntegerField()
    username = serializers.CharField(max_length=20)
    nickname = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=128)
    birth = serializers.DateField()

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # 유효하다면 nickname이 존재하는지 확인
        user = User.objects.filter(id=self.data['userId'], isDeleted='False')
        
        # 존재하지 않는다면 False, 404 반환
        if not user.exists():
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        updateUser = user.first()

        # 바꾸려는 닉네임이 중복된다면 False, 400 반환
        if updateUser.nickname is not self.data['nickname'] and User.objects.filter(nickname=self.data['nickname'], isDeleted='False').exists():
            return False, status.HTTP_400_BAD_REQUEST

        # 바꾸려는 이메일이 중복된다면 False, 400 반환
        if updateUser.email is not self.data['email'] and User.objects.filter(email=self.data['email'], isDeleted='False').exists():
            return False, status.HTTP_400_BAD_REQUEST

        return True, status.HTTP_200_OK


class UserResponse(serializers.Serializer):
    isSuccess = serializers.BooleanField()
    result = UserSerializer(source='*')


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