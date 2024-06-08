from rest_framework import serializers

from diary.models import Diary, Keywords


def exist_diary_id(diary_id):
    if not Diary.objects.filter(id=diary_id).exists():
        raise serializers.ValidationError(f'diaryId: {diary_id} 가 존재하지 않습니다.')


def not_exist_diary_date(user_id, date):
    if Diary.objects.filter(user_id=user_id, createDate=date).exists():
        raise serializers.ValidationError(f'이미 작성된 일기가 있습니다.')


def exist_keyword_id(keyword_id):
    if not Keywords.objects.filter(id=keyword_id).exists():
        raise serializers.ValidationError(f'keywordId: {keyword_id} 가 존재하지 않습니다.')
    

def positive_month_value(month):
    if month < 0 or month > 12:
        raise serializers.ValidationError(f'month의 입력이 잘못되었습니다.')


def positive_year_value(year):
    if len(str(year)) is not 4:
        raise serializers.ValidationError(f'year의 입력이 잘못되었습니다.')