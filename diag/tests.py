from rest_framework.test import APITestCase

from users.models import *
from diag.models import *

class TestDiag(APITestCase):
    def setUp(self):
        self.new_user = User.objects.create(**TEST_USER_DATA)
        self.new_user_id = self.new_user.id

        self.diag_record1 = DiagRecord.objects.create(user=self.new_user, total_score=10)
        self.diag_record2 = DiagRecord.objects.create(user=self.new_user, total_score=15)

    def test_diag_create(self):
        new_test_data = {
            "userId": self.new_user_id,
            "diagAnswer": [1] * 15
        }
        response = self.client.post('/api/diag', new_test_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['isSuccess'])

    def test_diag_get(self):
        response = self.client.get(f'/api/diag/record?userId={self.new_user_id}')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['isSuccess'])

        result = response.data['result']

        record1 = result[0]
        record2 = result[1]

        self.assertEqual(record1['id'], self.diag_record2.id)
        self.assertEqual(record1['totalScore'], self.diag_record2.total_score)

        self.assertEqual(record2['id'], self.diag_record1.id)
        self.assertEqual(record2['totalScore'], self.diag_record1.total_score)