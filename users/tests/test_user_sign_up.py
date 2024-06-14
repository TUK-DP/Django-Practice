from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

test_user_data = {
    "username": "test1",
    "nickname": "test1",
    "email": "test1@test1.com",
    "password": "test1",
    "birth": "2021-01-01"
}


class TestUserCreate(TestCase):
    def test_user_create(self):
        new_user = User.objects.create(**test_user_data)

        self.assertEqual(new_user.username, 'test1')
        self.assertEqual(new_user.nickname, 'test1')
        self.assertEqual(new_user.email, 'test1@test1.com')
        self.assertEqual(new_user.password, 'test1')
        self.assertEqual(new_user.birth, '2021-01-01')


class TestUserSignUp(APITestCase):
    def test_user_sign_up(self):
        response = self.client.post('/api/users/signup', test_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['isSuccess'], True)
        self.assertEqual(response.data['message'], 'OK')
        self.assertTrue('id' in response.data['result'])
