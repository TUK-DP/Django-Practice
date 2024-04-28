from rest_framework import serializers


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
