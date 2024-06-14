from django.test import TestCase
from rest_framework.exceptions import ValidationError

from users.models import User
from users.validator import not_exist_user_nickname, not_exist_user_email, validate_login

test_user_data = {
    "username": "test1",
    "nickname": "test1",
    "email": "test1@test1.com",
    "password": "test1",
    "birth": "2021-01-01"
}


class ValidatorTest(TestCase):
    def setUp(self):
        User.objects.create(**test_user_data)

    def test_not_exist_nickname(self):
        self.assertIsNone(not_exist_user_nickname(nickname='unique_nickname'))
        self.assertRaises(ValidationError, not_exist_user_nickname, nickname=test_user_data['nickname'])

    def test_not_exist_user_email(self):
        self.assertIsNone(not_exist_user_email(email='unique_email'))
        self.assertRaises(ValidationError, not_exist_user_email, email=test_user_data['email'])

    def test_validate_login(self):
        self.assertIsNone(validate_login(test_user_data['email'], test_user_data['password']))
        self.assertRaises(ValidationError, validate_login, 'unique_email', 'unique_password')
        