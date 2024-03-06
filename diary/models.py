from django.db import models

from config.basemodel import BaseModel


class Diary(BaseModel):
    title = models.CharField(max_length=100)

    # 이 ForeignKey는 다른 모델과의 관계를 나타낸다.
    # 대부분의 경우는 ForeignKey를 사용하게 될 것이다.
    # users앱의 model 중 User 모델과 연결되어 있다.
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    # __str__ 메서드는 자바의 toString()과 같은 역할을 한다.
    def __str__(self):
        return self.title

class Sentences(BaseModel):
    sentence = models.TextField()

    diary = models.ForeignKey('diary.Diary', related_name='sentences', on_delete=models.CASCADE)

class Keywords(BaseModel):
    keyword = models.CharField(max_length=100)

    sentence = models.ForeignKey('diary.Sentences', related_name='keywords', on_delete=models.CASCADE)

class Questions(BaseModel):
    question = models.TextField()

    keyword = models.ForeignKey('diary.Keywords', related_name='questions', on_delete=models.CASCADE)