from rest_framework import serializers


def positive_value(value):
    if value <= 0:
        raise serializers.ValidationError('양수만 입력 가능합니다.')



