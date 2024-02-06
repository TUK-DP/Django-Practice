from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.views.decorators.csrf import csrf_exempt


def index(request: WSGIRequest):
    return HttpResponse("Users Index Page")