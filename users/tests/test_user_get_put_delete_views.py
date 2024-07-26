from rest_framework.test import APITestCase

from users.models import User
from users.token_handler import create_token, decode_token

from config.test_data import TEST_USER_DATA


class GetPutDeleteTest(APITestCase):
    def setUp(self):
        new_user = User.objects.create(**TEST_USER_DATA)
        self.new_user_id = new_user.id
        self.token_serializer = create_token(userId=new_user.id)
        new_user.refresh_token = self.token_serializer.data.get("RefreshToken")
        new_user.save()

    def test_get_user_by_userId(self):
        response = self.client.get(
            f'/api/users/{self.new_user_id}',
            headers={
                "AccessToken": self.token_serializer.data.get("AccessToken")
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['isSuccess'])
        self.assertEqual(response.data['result']['id'], self.new_user_id)

    def test_put_user_by_userId(self):
        update_data = {
            "id": self.new_user_id,
            "accountId": "test2",
            "password": "test2",
            "username": "test"
        }

        response = self.client.put(
            f'/api/users', update_data, headers={
                "AccessToken": self.token_serializer.data.get("AccessToken")
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['isSuccess'])
        self.assertEqual(response.data['result']['id'], self.new_user_id)

    def test_delete_user_by_userId(self):
        response = self.client.delete(
            f'/api/users/{self.new_user_id}',
            headers={
                "AccessToken": self.token_serializer.data.get("AccessToken")
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['isSuccess'])

