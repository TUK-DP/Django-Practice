from rest_framework import status
from rest_framework.test import APITestCase

from users.models import TEST_USER_DATA


class TestUserSignUp(APITestCase):
    def test_user_sign_up(self):
        mapped_data = {
            "accountId": TEST_USER_DATA["account_id"],
            "password": TEST_USER_DATA["password"],
            "username": TEST_USER_DATA["username"]
        }
        
        response = self.client.post('/api/users/signup', mapped_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['isSuccess'], True)
        self.assertEqual(response.data['message'], 'OK')
        self.assertTrue('id' in response.data['result'])
