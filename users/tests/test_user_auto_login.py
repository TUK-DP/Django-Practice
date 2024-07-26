import json

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User, TEST_USER_DATA
from users.token_handler import create_token

# Create your tests here.


class TestUserAutoLogin(APITestCase):
    def setUp(self):
        new_user = User.objects.create(**TEST_USER_DATA)
        self.new_user_id = new_user.id
        self.token_serializer = create_token(userId=new_user.id)
        new_user.refresh_token = self.token_serializer.data.get("RefreshToken")
        new_user.save()

    def test_when_success_user_auto_login(self):
        find_user = User.objects.first()

        response = self.client.get(
            f'/api/users/{find_user.id}/auto/login',
            headers={
                "AccessToken": self.token_serializer.data.get("AccessToken"),
                "RefreshToken": self.token_serializer.data.get("RefreshToken")
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['isSuccess'])
        self.assertTrue('token' in response.data['result'])

        expect_token = self.token_serializer.data
        actual_token = response.data['result']['token']

        self.assertDictEqual(expect_token, actual_token)
        self.assertJSONEqual(
            json.dumps(expect_token),
            json.dumps(actual_token)
        )

    def test_when_fail_user_auto_login(self):
        response = self.client.get(
            f'/api/users/{self.new_user_id}/auto/login',
            headers={
                "AccessToken": self.token_serializer.data.get("AccessToken"),
                "RefreshToken": "wrong_refresh_token"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['isSuccess'])
