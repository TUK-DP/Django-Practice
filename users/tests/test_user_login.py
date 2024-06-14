from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.token_handler import create_token

# Create your tests here.

test_user_data = {
    "username": "test1",
    "nickname": "test1",
    "email": "test1@test1.com",
    "password": "test1",
    "birth": "2021-01-01"
}


class TestUserLogin(APITestCase):
    def setUp(self):
        User.objects.create(**test_user_data)

    def test_user_login(self):
        response = self.client.post('/api/users/login', {
            "email": test_user_data['email'],
            "password": test_user_data['password']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['isSuccess'])

        self.assertTrue(
            response.data['result']['token'],
            create_token(userId=response.data['result']['user']['id']).data
        )
