from django.db import models
from django.http import JsonResponse
from rest_framework import status
from rest_framework.request import Request

from config.settings import REQUEST_BODY, REQUEST_QUERY, REQUEST_HEADER, REQUEST_PATH


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class ApiResponse:
    @staticmethod
    def on_success(result=None, message=None, response_status=status.HTTP_200_OK):
        if not result:
            return JsonResponse({'isSuccess': True, "message": message}, status=response_status)
        return JsonResponse({'isSuccess': True, 'result': result}, status=response_status)

    @staticmethod
    def on_fail(message, response_status=status.HTTP_400_BAD_REQUEST):
        return JsonResponse({'isSuccess': False, 'message': message}, status=response_status)


def validator(request_serializer=None, request_type=REQUEST_BODY, return_key="serializer", **path_args):
    """
    :param request_serializer: 유효성검사를 원하는 serializer를 입력받음
    :param request_type: 어떤 방식으로 데이터를 받을지 선택
    :param return_key: request에 저장할 key값
    """
    def decorator(fuc):
        def decorated_func(self, request: Request, *args, **kwargs):
            response_serializer = request_serializer(data=request.data)

            if request_type == REQUEST_QUERY:
                response_serializer = request_serializer(data=request.query_params)

            elif request_type == REQUEST_PATH:
                data = {key: kwargs.get(key) for key in request_serializer().fields.keys()}
                response_serializer = request_serializer(data=data)

            elif request_type == REQUEST_HEADER:
                data = {key: request.headers.get(key) for key in request_serializer().fields.keys()}
                response_serializer = request_serializer(data=data)

            if not response_serializer.is_valid():
                return ApiResponse.on_fail(
                    response_serializer.errors
                )

            setattr(request, return_key, response_serializer)

            return fuc(self, request, *args, **kwargs)

        return decorated_func

    return decorator
