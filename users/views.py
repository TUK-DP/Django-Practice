import json

from django.forms import model_to_dict
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.csrf import csrf_exempt

from users.models import User


def index(request: WSGIRequest):
    return HttpResponse("Users Index Page")


def findAll(request: WSGIRequest) -> HttpResponse:
    # Users.objects.all() => select * from users
    objects_all = User.objects.all()

    # Convert QuerySet to List
    l = list(map(model_to_dict, objects_all))

    print(l)

    if request.method == "GET":
        return HttpResponse(l)


def save(request: WSGIRequest) -> HttpResponse:
    if request.method == "POST":
        body = json.loads(request.body)

        username = body["username"]
        email = body["email"]

        newUser = User(username=username, email=email)
        newUser = User.objects.create(username=newUser.username, email=newUser.email)

        to_dict = model_to_dict(newUser)

        return HttpResponse(to_dict)
