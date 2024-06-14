from django.test import TestCase, Client
from rest_framework import status

from users.models import User


# Create your tests here.

class UserSignUpTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_data = {
            "username": "test1",
            "nickname": "test1",
            "email": "test1@test1.com",
            "password": "test1",
            "birth": "2021-01-01"
        }

    def test_user_create(self):
        new_user = User.objects.create(**self.test_data)

        self.assertEqual(new_user.username, 'test1')
        self.assertEqual(new_user.nickname, 'test1')
        self.assertEqual(new_user.email, 'test1@test1.com')
        self.assertEqual(new_user.password, 'test1')
        self.assertEqual(new_user.birth, '2021-01-01')

    def test_user_sign_up(self):
        response = self.client.post('/api/users/signup', self.test_data)

        new_user_id = len(User.objects.all()) + 1

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = response.json()

        self.assertEqual(response['isSuccess'], True)
        self.assertEqual(response['message'], 'OK')

        self.assertEqual(response['result']['id'], new_user_id)
