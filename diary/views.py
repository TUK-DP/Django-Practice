import json

from django.core.handlers.wsgi import WSGIRequest
from django.forms import model_to_dict
from django.http import HttpResponse

from diary.models import Diary
from users.models import User


def findAll(request: WSGIRequest) -> HttpResponse:
    if request.method == "GET":
        objects_all = Diary.objects.all()

        l = list(map(model_to_dict, objects_all))

        return HttpResponse(l)


def save(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        # Post Body에 있는 userId로 User 조회

        body = json.loads(request.body)

        userId = body["userId"]

        print(body)
        findUser = User.objects.get_queryset().get(id=userId)

        print(model_to_dict(findUser))

        diary = Diary(title=body["title"], content=body["content"], user=findUser)
        newDiary = Diary.objects.create(title=diary.title, content=diary.content, user=diary.user)
        print(newDiary)

        return HttpResponse(model_to_dict(newDiary))
