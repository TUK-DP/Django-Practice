from django.db import models

from config.basemodel import BaseModel


# Create your models here.
class User(BaseModel):
    account_id = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128, null=True)
    username = models.CharField(max_length=20, null=True)
    refresh_token = models.CharField(max_length=128, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

TEST_USER_DATA = {
    "account_id": "test",
    "password": "test",
    "username": "test"
}