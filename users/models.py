from django.db import models

from config.basemodel import BaseModel


# Create your models here.
class Users(BaseModel):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        return self.username
