from config.sort_options import *
from config.validator import positive_value
from diary.validator import *
from users.models import User
from users.validator import exist_user_id


class GetDiaryByIdRequest(serializers.Serializer):
    diaryId = serializers.IntegerField(validators=[exist_diary_id])


class GetDiaryByDateRequest(serializers.Serializer):
    date = serializers.DateField(required=False, help_text='YYYY-MM-DD 형식으로 입력해주세요.')


class CheckDiaryEntriesRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    year = serializers.IntegerField(validators=[positive_year])
    month = serializers.IntegerField(validators=[positive_month])


class GetDiaryByUserAndDateRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    startDate = serializers.DateField()
    finishDate = serializers.DateField()

    sortBy = serializers.ChoiceField(
        choices=[key for key in DATE_SORT_MAPPER.keys()],
        required=False,
        default=DES_CREATEDATE,
        validators=[positive_sort_by]
    )


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
    

class GetDiaryPagingRequset(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
    page = serializers.IntegerField(validators=[positive_value])
    pageSize = serializers.IntegerField(validators=[positive_value])
