from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserSerializer, UserCreateRequest


class UserView(APIView):
    def get(self, request: WSGIRequest) -> HttpResponse:
        findUsers = User.objects.all()
        serializer = UserSerializer(findUsers, many=True)
        return JsonResponse(serializer.data, safe=False)

    @csrf_exempt
    def post(self, request: WSGIRequest) -> HttpResponse:
        data = JSONParser().parse(request)
        request = UserCreateRequest(data=data)
        if request.is_valid():
            newUser = request.to_user()
            return JsonResponse(newUser.data, status=201)
        return JsonResponse(request.errors, status=400)
