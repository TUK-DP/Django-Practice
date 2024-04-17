from django.db import models

from config.basemodel import BaseModel


# Create your models here.
class User(BaseModel):
    nickname = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128, null=True)
    username = models.CharField(max_length=20, null=True)
    birth = models.DateField(null=True)
    isDeleted = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
