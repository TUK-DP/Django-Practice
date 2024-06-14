from rest_framework.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.validator import not_exist_user_nickname, not_exist_user_email

test_user_data = {
    "username": "test1",
    "nickname": "test1",
    "email": "test1@test1.com",
    "password": "test1",
    "birth": "2021-01-01"
}


class TestUserSignUp(APITestCase):
    def test_user_sign_up(self):
        response = self.client.post('/api/users/signup', test_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['isSuccess'], True)
        self.assertEqual(response.data['message'], 'OK')
        self.assertTrue('id' in response.data['result'])


class TestValidator(TestCase):
    def setUp(self):
        User.objects.create(**test_user_data)

    def test_not_exist_nickname(self):
        self.assertIsNone(not_exist_user_nickname(nickname='unique_nickname'))
        self.assertRaises(ValidationError, not_exist_user_nickname, nickname=test_user_data['nickname'])

    def test_not_exist_user_email(self):
        self.assertIsNone(not_exist_user_email(email='unique_email'))
        self.assertRaises(ValidationError, not_exist_user_email, email=test_user_data['email'])
