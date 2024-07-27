from rest_framework.test import APITestCase

from users.models import *
from diag.models import *


class TestUserDiag(APITestCase):
    def setUp(self):
        new_user = User.objects.create(**TEST_USER_DATA)
        self.new_user_id = new_user.id

        TEST_DIAG_DATA['user'] = new_user

        self.new_diag_record = DiagRecord.objects.create(**TEST_DIAG_DATA)

    def test_diag_create(self):
        new_test_data = {k: v for k, v in TEST_DIAG_DATA.items()}
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
