from rest_framework.exceptions import ValidationError

from users.models import User


def exist_user_id(user_id: int = 0):
    if not User.objects.filter(id=user_id, is_deleted=False).exists():
        raise ValidationError('존재하지 않는 사용자입니다.')


def exist_user_account_id(account_id: str = 'account_id'):
    if not User.objects.filter(account_id=account_id).exists():
        raise ValidationError('존재하지 않는 사용자입니다.')


def not_exist_user_account_id(account_id: str = 'account_id'):
    if User.objects.filter(account_id=account_id).exists():
        raise ValidationError('이미 존재하는 아이디입니다.')


def validate_login(account_id: str, pass_word: str):
    if not User.objects.filter(account_id=account_id, pass_word=pass_word, is_deleted=False).exists():
        raise ValidationError('존재하지 않는 사용자입니다.')


def validate_update(id, account_id):
    find_user = User.objects.get(id=id)
    if find_user.account_id != account_id:
        not_exist_user_account_id(account_id)
