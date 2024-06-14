from django.db.models import QuerySet

from diary.serialziers.keyword_serializers import KeywordResponse
from diary.validator import *
from users.serializers.user_get_post_put_delete_serializers import *


class DiarySerializer(serializers.ModelSerializer):
    user = UserSafeSerializer(read_only=True)

    class Meta:
        model = Diary
        fields = '__all__'


class DiaryResultResponse(serializers.ModelSerializer):
    diaryId = serializers.IntegerField(source="id")

    class Meta:
        model = Diary
        fields = ['diaryId', 'title', 'createDate', 'content', 'imgUrl']


class GetDiaryByIdResponse(serializers.Serializer):
    diaryId = serializers.IntegerField(source='id')
    title = serializers.CharField()
    createDate = serializers.DateField()
    content = serializers.CharField()
    keywords = KeywordResponse(many=True)
    imgUrl = serializers.CharField()

    @staticmethod
    def to_json(diary: Diary):
        return {
            'diaryId': diary.id,
            'title': diary.title,
            'createDate': diary.createDate,
            'content': diary.content,
            'keywords': [KeywordResponse.to_json(keyword) for keyword in diary.keywords.all()],
            'imgUrl': diary.imgUrl
        }


class GetDiaryPreviewResponse(serializers.Serializer):
    diaryId = serializers.IntegerField(source='id')
    title = serializers.CharField()
    createDate = serializers.DateField()
    content = serializers.CharField()

    @staticmethod
    def to_json(diary: Diary):
        return {
            'diaryId': diary.id,
            'title': diary.title,
            'createDate': diary.createDate,
            'content': diary.content
        }


class GetDiariesByUserAndDateResponse(serializers.Serializer):
    user = UserSafeSerializer()
    diaries = GetDiaryByIdResponse(many=True)

    @staticmethod
    def to_json(user: User, diaries: QuerySet):
        return {
            'user': UserSafeSerializer(user).data,
            'diaries': [GetDiaryPreviewResponse.to_json(diary) for diary in diaries]
        }
