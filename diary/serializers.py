from rest_framework import status

from config.validator import positive_value
from users.models import User
from users.serializers import UserSafeSerializer
from users.validator import exist_user_id
from .models import Questions
from .validator import *


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


class KeywordSerializer(serializers.ModelSerializer):
    sentence = DiarySerializer(read_only=True)

    class Meta:
        model = Keywords
        fields = '__all__'


class KeywordResultSerializer(serializers.ModelSerializer):
    keywordId = serializers.IntegerField(source="id")

    class Meta:
        model = Keywords
        fields = ['keywordId', 'keyword', 'imgUrl']


class QuestionSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(read_only=True)

    class Meta:
        model = Questions
        fields = '__all__'


class DiaryCreateRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
    date = serializers.DateField()

    def validate(self, attrs):
        not_exist_diary_date(attrs['userId'], attrs['date'])
        return attrs

    def create(self, validated_data):
        return Diary.objects.create(
            user_id=validated_data['userId'],
            title=validated_data['title'],
            content=validated_data['content'],
            createDate=validated_data['date']
        )


class DiaryUpdateRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    title = serializers.CharField(max_length=100, required=False)
    content = serializers.CharField(required=False)
    date = serializers.DateField(required=False)

    def validate(self, attrs):
        if 'date' in attrs:
            not_exist_diary_date(attrs['userId'], attrs['date'])
        return attrs

    def update(self, instance, validated_data):
        title = validated_data.get('title', instance.title)
        content = validated_data.get('content', instance.content)
        createDate = validated_data.get('date', instance.createDate)
        userId = validated_data.get('userId', instance.user_id)
        
        instance.delete()
        Diary.objects.filter(id=instance.id).delete()

        return Diary.create(
            user=User.objects.get(id=userId),
            title=title,
            content=content,
            createDate=createDate
        )


class GetUserRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])


class GetDiaryRequest(serializers.Serializer):
    diaryId = serializers.IntegerField(validators=[exist_diary_id])


class GetDiaryByDateRequest(serializers.Serializer):
    date = serializers.DateField(required=False, help_text='YYYY-MM-DD 형식으로 입력해주세요.')


class GetNodeDataRequest(serializers.Serializer):
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
        is_diary_exist = Diary.objects.filter(id=self.data['diaryId'],
                                              user=User.objects.get(id=self.data['userId'])).exists()
        # 존재하지 않는다면 False, 404 반환
        if not is_diary_exist:
            self._errors['diaryId'] = [f'diaryId: {self.data.get("diaryId")} 가 존재하지 않습니다.']
            return False, status.HTTP_404_NOT_FOUND

        return True, status.HTTP_200_OK


class KeywordIdRequest(serializers.Serializer):
    keywordId = serializers.IntegerField(validators=[exist_keyword_id])


class ImageUrlRequest(serializers.Serializer):
    imgUrl = serializers.CharField()


class FindKeywordImgRequest(serializers.Serializer):
    keyword = serializers.CharField()
    page = serializers.IntegerField(validators=[positive_value])
    pageSize = serializers.IntegerField(validators=[positive_value])


class AnswerSerializer(serializers.Serializer):
    keywordId = serializers.IntegerField(validators=[exist_keyword_id])
    answer = serializers.CharField(allow_blank=True)


class AnswerListRequest(serializers.Serializer):
    answers = AnswerSerializer(many=True)


class IsExistDiaryRequest(serializers.Serializer):
    userId = serializers.IntegerField()
    year = serializers.IntegerField()
    month = serializers.IntegerField()


class GetDiaryByUserAndDateRequest(serializers.Serializer):
    userId = serializers.IntegerField()
    startDate = serializers.DateField()
    finishDate = serializers.DateField()