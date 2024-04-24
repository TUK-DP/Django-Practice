from django.db import models
from django.http import JsonResponse
from rest_framework import status


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


def validator(request_serializer=None):
    def decorator(fuc):
        def decorated_func(self, request):
            requestSerial = request_serializer(data=request.data)

            isValid = requestSerial.is_valid()

            # 유효성 검사 통과하지 못한 경우
            if not isValid:
                return ApiResponse.on_fail(
                    requestSerial.errors
                )

            return fuc(self, request)

        return decorated_func

    return decorator
