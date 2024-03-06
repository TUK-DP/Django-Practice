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
    def on_success(result, response_status=status.HTTP_200_OK):
        return JsonResponse({'isSuccess': True, 'result': result}, status=response_status)

    @staticmethod
    def on_fail(message, response_status=status.HTTP_400_BAD_REQUEST):
        return JsonResponse({'isSuccess': False, 'message': message}, status=response_status)
