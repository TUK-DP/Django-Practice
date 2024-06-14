from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.token_handler import decode_token

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
        self.new_user = User.objects.create(**test_user_data)

    def test_when_success_user_login(self):
        response = self.client.post('/api/users/login', {
            "email": test_user_data['email'],
            "password": test_user_data['password']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['isSuccess'])

        is_valid, message, access_token = decode_token(response.data['result']['token']['AccessToken'])
        self.assertTrue(is_valid)
        self.assertEqual(access_token['userId'], str(self.new_user.id))

    def test_when_fail_user_login(self):
        response = self.client.post('/api/users/login', {
            "email": test_user_data['email'],
            "password": "wrong_password"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['isSuccess'])
