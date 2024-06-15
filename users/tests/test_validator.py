from django.test import TestCase
from rest_framework.exceptions import ValidationError

from users.models import User
from users.token_handler import validate_user_id_token, create_token, decode_token
from users.token_serializer import TokenSerializer
from users.validator import *

test_user_data = {
    "username": "test1",
    "nickname": "test1",
    "email": "test1@test1.com",
    "password": "test1",
    "birth": "2021-01-01"
}


class ValidatorTest(TestCase):
    def setUp(self):
        self.new_user = User.objects.create(**test_user_data)
        self.token = create_token(userId=self.new_user.id)

    def test_not_exist_nickname(self):
        self.assertIsNone(not_exist_user_nickname(nickname='unique_nickname'))
        self.assertRaises(ValidationError, not_exist_user_nickname, nickname=test_user_data['nickname'])

    def test_not_exist_user_email(self):
        self.assertIsNone(not_exist_user_email(email='unique_email'))
        self.assertRaises(ValidationError, not_exist_user_email, email=test_user_data['email'])

    def test_exist_user_email(self):
        self.assertIsNone(exist_user_email(email=test_user_data['email']))
        self.assertRaises(ValidationError, exist_user_email, email='unique_email')

    def test_validate_login(self):
        self.assertIsNone(validate_login(test_user_data['email'], test_user_data['password']))
        self.assertRaises(ValidationError, validate_login, 'unique_email', 'unique_password')

    def test_exist_user_id(self):
        self.assertIsNone(exist_user_id(user_id=User.objects.first().id))
        self.assertRaises(ValidationError, exist_user_id, user_id=0)

    def test_decode_token(self):
        actual_access_token = self.token.data.get('AccessToken')
        actual_refresh_token = self.token.data.get('RefreshToken')

        is_valid, message, access_token = decode_token(actual_access_token)
        self.assertTrue(is_valid)
        self.assertEqual(access_token['userId'], str(self.new_user.id))

        is_valid, message, refresh_token = decode_token(actual_refresh_token)
        self.assertTrue(is_valid)
        self.assertEqual(refresh_token['userId'], str(self.new_user.id))

    def test_validate_user_id_token(self):
        actual_access_token = self.token.data.get('AccessToken')
        actual_refresh_token = self.token.data.get('RefreshToken')

        _, _, decoded_access_token = decode_token(actual_access_token)
        _, _, decoded_refresh_token = decode_token(actual_refresh_token)

        is_valid, _ = validate_user_id_token(decoded_access_token, self.new_user.id)
        self.assertTrue(is_valid)

        is_valid, _ = validate_user_id_token(decoded_refresh_token, self.new_user.id)
        self.assertTrue(is_valid)

        is_valid, _ = validate_user_id_token({"userId": str(self.new_user.id)}, 0)
        self.assertFalse(is_valid)
