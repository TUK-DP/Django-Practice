from rest_framework.exceptions import ValidationError

from users.models import User


def exist_user(user_id: int = 0):
    if not User.objects.filter(id=user_id).exists():
        raise ValidationError('존재하지 않는 사용자입니다.')


def exist_email(email: str = 'email'):
    if not User.objects.filter(email=email).exists():
        raise ValidationError('존재하지 않는 사용자입니다.')


def not_exist_nickname(nickname: str = 'nickname'):
    if User.objects.filter(nickname=nickname).exists():
        raise ValidationError('이미 존재하는 닉네임입니다.')


def not_exist_email(email: str = 'email'):
    if User.objects.filter(email=email).exists():
        raise ValidationError('이미 존재하는 이메일입니다.')
