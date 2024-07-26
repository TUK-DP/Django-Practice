from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, TEST_USER_DATA
from users.token_handler import decode_token

# Create your tests here.


class TestUserLogin(APITestCase):
    def setUp(self):
        self.new_user = User.objects.create(**TEST_USER_DATA)

    def test_when_success_user_login(self):
        response = self.client.post('/api/users/login', {
            "accountId": TEST_USER_DATA['account_id'],
            "password": TEST_USER_DATA['password']
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['isSuccess'])

        is_valid, message, access_token = decode_token(response.data['result']['token']['AccessToken'])
        self.assertTrue(is_valid)
        self.assertEqual(access_token['userId'], str(self.new_user.id))

    def test_when_fail_user_login(self):
        response = self.client.post('/api/users/login', {
            "accountId": TEST_USER_DATA['account_id'],
            "password": "wrong password"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['isSuccess'])
