import json

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


class TestUserAutoLogin(APITestCase):
    def setUp(self):
        new_user = User.objects.create(**test_user_data)
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

        self.assertJSONEqual(
            json.dumps(response.data['result']['token']),
            json.dumps(create_token(userId=response.data['result']['user']['id']).data)
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
