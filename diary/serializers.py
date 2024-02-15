from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer
from .models import Diary


class DiarySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Diary
        fields = ('id', 'title', 'content', 'user', 'created_at', 'updated_at')


class DiaryCreateRequest(serializers.ModelSerializer):
    userId = serializers.IntegerField()

    class Meta:
        model = Diary
        fields = ('userId', 'title', 'content')

    def to_diary(self, user: User) -> DiarySerializer:
        newDiary = DiarySerializer(data={'title': self.data["title"], 'content': self.data["content"], 'user': user})
        newDiary.is_valid()
        newDiary.save(user=user)
        return newDiary

class WriteRequest(serializers.Serializer):
    userId = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()

    class Meta:
        model = Diary
        fields = '__all__'

    def create(self, validated_data):
        user_id = validated_data.pop('userId')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("유저가 존재하지 않습니다.")
        
        validated_data['user'] = user
        return Diary.objects.create(**validated_data)
        