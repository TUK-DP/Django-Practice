from rest_framework.test import APITestCase

from users.models import User, DiagRecord

test_user_data = {
    "username": "test1",
    "nickname": "test1",
    "email": "test1@test1.com",
    "password": "test1",
    "birth": "2021-01-01"
}

test_diag_data = {
    "totalQuestionSize": 12,
    "yesCount": 3,
}


class TestUserDiag(APITestCase):
    def setUp(self):
        new_user = User.objects.create(**test_user_data)
        self.new_user_id = new_user.id

        test_diag_data['user'] = new_user

        self.new_diag_record = DiagRecord.objects.create(**test_diag_data)

    def test_diag_create(self):
        new_test_data = {k: v for k, v in test_diag_data.items()}
        new_test_data['userId'] = self.new_user_id
        response = self.client.post(
            f'/api/users/recordsave',
            new_test_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['isSuccess'])

    def test_diag_get(self):
        response = self.client.get(
            f'/api/users/prevrecord?userId={self.new_user_id}',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['isSuccess'])
        self.assertEqual(response.data['result']['id'], self.new_diag_record.id)
        self.assertEqual(response.data['result']['user'], self.new_diag_record.user.id)
        self.assertEqual(response.data['result']['totalQuestionSize'], self.new_diag_record.totalQuestionSize)
        self.assertEqual(response.data['result']['yesCount'], self.new_diag_record.yesCount)
