from rest_framework import serializers

from users.validator import *

class DuplicateAccountIdRequest(serializers.Serializer):
    accountId = serializers.CharField(max_length=128, validators=[not_exist_user_account_id])