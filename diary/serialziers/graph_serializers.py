from rest_framework import status

from diary.validator import *
from users.models import User


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


class UserNode(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    label = serializers.CharField(help_text='User')
    text = serializers.CharField()


class DiaryNode(serializers.Serializer):
    id = serializers.IntegerField()
    diary_id = serializers.IntegerField()
    label = serializers.CharField(help_text='Diary')
    text = serializers.CharField()


class KeywordNode(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField(help_text='Keyword')
    text = serializers.CharField()
    weight = serializers.FloatField()


class Property(serializers.Serializer):
    tfidf = serializers.FloatField()


class Relationships(serializers.Serializer):
    properties = Property()
    type = serializers.CharField(help_text='INCLUDE|CONNECTED|WROTE')
    startNode = serializers.IntegerField()
    endNode = serializers.IntegerField()


class GraphDataSerializer(serializers.Serializer):
    User = UserNode()
    Diary = DiaryNode()
    # [UserNode(), DiaryNode(), KeywordNode()]
    nodes = serializers.ListField(child=serializers.DictField(help_text='UserNode|DiaryNode|KeywordNode'))
    relationships = Relationships()
