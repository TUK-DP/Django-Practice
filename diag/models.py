from django.db import models

from config.basemodel import BaseModel

# Create your models here.

class DiagRecord(BaseModel):
    total_score = models.IntegerField()

    user = models.ForeignKey('users.User', related_name='diagrecord', on_delete=models.CASCADE)

TEST_DIAG_DATA = {
    "total_score": 12,
}