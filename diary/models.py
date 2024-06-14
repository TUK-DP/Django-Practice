from django.db import models

from config.basemodel import BaseModel
from diary.utils.graph.graph import GraphDB
from diary.utils.text_rank.textrank import TextRank, make_quiz


class Diary(BaseModel):
    title = models.CharField(max_length=100)

    createDate = models.DateField()
    content = models.TextField()
    imgUrl = models.TextField(null=True)

    # 이 ForeignKey는 다른 모델과의 관계를 나타낸다.
    # 대부분의 경우는 ForeignKey를 사용하게 될 것이다.
    # users앱의 model 중 User 모델과 연결되어 있다.
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    # __str__ 메서드는 자바의 toString()과 같은 역할을 한다.
    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        conn = GraphDB()
        conn.delete_diary(user_id=self.user.id, diary_id=self.id)
        return self

    @staticmethod
    def create(user=None, title=None, content=None, createDate=None, img_url=None):
        newDiary = Diary.objects.create(user=user, title=title, content=content, createDate=createDate, imgUrl=img_url)

        conn = GraphDB()
        memory = TextRank(content=content)

        # GraphDB에 추가
        conn.create_and_link_nodes(
            user_id=newDiary.user.id, diary_id=newDiary.id,
            words_graph=memory.words_graph,
            words_dict=memory.words_dict,
            weights_dict=memory.weights_dict
        )

        # 키워드 추출 후 가중치가 높은 키워드 5개로 퀴즈 생성
        question, keyword = make_quiz(memory, keyword_size=5)

        # 각 키워드별로 Question 생성
        for q, k in zip(question, keyword):
            newKeyword = Keywords.objects.create(keyword=k, diary=newDiary)
            Questions.objects.create(question=q, keyword=newKeyword)

        return newDiary


class Keywords(BaseModel):
    keyword = models.CharField(max_length=100)
    imgUrl = models.TextField(null=True)

    diary = models.ForeignKey('diary.Diary', related_name='keywords', on_delete=models.CASCADE)


class Questions(BaseModel):
    question = models.TextField()

    keyword = models.ForeignKey('diary.Keywords', related_name='questions', on_delete=models.CASCADE)
