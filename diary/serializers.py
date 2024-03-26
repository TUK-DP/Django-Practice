from rest_framework import serializers, status

from users.models import User
from users.serializers import UserSafeSerializer
from .models import Diary, Keywords, Questions


class DiarySerializer(serializers.ModelSerializer):
    user = UserSafeSerializer(read_only=True)

    class Meta:
        model = Diary
        fields = '__all__'


class DiaryResultResponse(serializers.ModelSerializer):
    diaryId = serializers.IntegerField(source="id")

    class Meta:
        model = Diary
        fields = ['diaryId', 'title', 'createDate', 'content']


class KeywordSerializer(serializers.ModelSerializer):
    sentence = DiarySerializer(read_only=True)

    class Meta:
        model = Keywords
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(read_only=True)

    class Meta:
        model = Questions
        fields = '__all__'


class DiaryCreateRequest(serializers.ModelSerializer):
    userId = serializers.IntegerField()

    class Meta:
        model = Diary
        fields = ('userId', 'title')

    def to_diary(self, user: User) -> DiarySerializer:
        newDiary = DiarySerializer(data={'title': self.data["title"], 'user': user})
        newDiary.is_valid()
        newDiary.save(user=user)
        return newDiary


class WriteRequest(serializers.Serializer):
    userId = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
    date = serializers.DateField()

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # 유효하다면 userId가 존재하는지 확인
        is_user_exist = User.objects.filter(id=self.data['userId']).exists()

        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        # 존재한다면 date에 일기가 존재하는지 확인
        is_already_diary = Diary.objects.filter(createDate=self.data['date'], user=User.objects.get(id=self.data['userId'])).exists()

        # 존재한다면 False, 400 반환
        if is_already_diary:
            self._errors['date'] = [f'date: 이미 일기가 존재합니다.']
            return False, status.HTTP_400_BAD_REQUEST

        return True, status.HTTP_200_OK


class UpdateRequest(serializers.Serializer):
    diaryId = serializers.IntegerField()
    userId = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
    date = serializers.DateField()

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # userId가 존재하는지 확인
        is_user_exist = User.objects.filter(id=self.data['userId']).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        # diaryId가 존재하는지 확인
        is_diary_exist = Diary.objects.filter(id=self.data['diaryId']).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_diary_exist:
            self._errors['diaryId'] = [f'diaryId: {self.data.get("diaryId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK


class GetUserRequest(serializers.Serializer):
    userId = serializers.IntegerField()

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # userId가 존재하는지 확인
        is_user_exist = User.objects.filter(id=self.data['userId']).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK


class GetDiaryRequest(serializers.Serializer):
    diaryId = serializers.IntegerField()

    def is_valid(self, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # diaryId가 존재하는지 확인
        is_diary_exist = Diary.objects.filter(id=self.data['diaryId']).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_diary_exist:
            self._errors['diaryId'] = [f'diaryId: {self.data.get("diaryId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK
    
class GetDiaryByDateRequest(serializers.Serializer):
    userId = serializers.IntegerField()
    date = serializers.DateField()

    def is_valid(self, *, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST
        
        # userId가 존재하는지 확인
        is_user_exist = User.objects.filter(id=self.data['userId']).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        # 날짜에 작성된 일기가 있는지 확인
        is_diary_exist = Diary.objects.filter(user=User.objects.get(id=self.data['userId']), createDate=self.data['date']).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_diary_exist:
            self._errors['diaryId'] = [f'작성된 일기가 없습니다.']
            return False, status.HTTP_404_NOT_FOUND
        
        return True, status.HTTP_200_OK

class DeleteDiaryRequest(serializers.Serializer):
    userId = serializers.IntegerField()
    diaryId = serializers.IntegerField()

    def is_valid(self, *, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST
        
        # userId가 존재하는지 확인
        is_user_exist = User.objects.filter(id=self.data['userId']).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_user_exist:
            self._errors['userId'] = [f'userId: {self.data.get("userId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        # diaryId가 존재하는지 확인
        is_diary_exist = Diary.objects.filter(id=self.data['diaryId'], user=User.objects.get(id=self.data['userId'])).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_diary_exist:
            self._errors['diaryId'] = [f'diaryId: {self.data.get("diaryId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK