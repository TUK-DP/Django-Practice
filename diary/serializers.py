from rest_framework import serializers

from users.models import User
from users.serializers import UserSafeSerializer
from .models import Diary, Sentences, Quizs


class DiarySerializer(serializers.ModelSerializer):
    user = UserSafeSerializer(read_only=True)

    class Meta:
        model = Diary
        fields = '__all__'

class DiarySimpleSerializer(serializers.ModelSerializer):
    user = UserSafeSerializer(read_only=True)

    class Meta:
        model = Diary
        fields = ['id', 'user', 'title']

class SentenceSerializer(serializers.ModelSerializer):
    diay = DiarySerializer(read_only=True)

    class Meta:
        model = Sentences
        fields = '__all__'

class SentenceSimpleSerializer(serializers.ModelSerializer):
    diary = DiarySimpleSerializer(read_only=True)

    class Meta:
        model = Sentences
        fields = ['id', 'diary', 'sentence']

class QuizSerializer(serializers.ModelSerializer):
    sentences = SentenceSerializer(read_only=True)

    class Meta:
        model = Quizs
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

class UpdateRequest(serializers.Serializer):
    diaryId = serializers.IntegerField()
    userId = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()

class GetUserRequest(serializers.Serializer):
    userId = serializers.IntegerField()

class GetDiaryRequest(serializers.Serializer):
    diaryId = serializers.IntegerField()