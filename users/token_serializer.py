from rest_framework import serializers

from users.validator import exist_user_id


class TokenSerializer(serializers.Serializer):
    ACCESS_TOKEN = 'AccessToken'
    REFRESH_TOKEN = 'RefreshToken'

    AccessToken = serializers.CharField(validators=[])
    RefreshToken = serializers.CharField(validators=[])

    @staticmethod
    def to_validated_serializer(access_token: str, refresh_token: str) -> 'TokenSerializer':
        serializer = TokenSerializer(data={
            TokenSerializer.ACCESS_TOKEN: access_token,
            TokenSerializer.REFRESH_TOKEN: refresh_token
        })
        if not serializer.is_valid():
            print(serializer.errors)
            raise ValueError("TokenSerializer is not valid")

        return serializer

    @staticmethod
    def to_json(access_token=None, refresh_token=None):
        return {
            "AccessToken": access_token,
            "RefreshToken": refresh_token
        }


class AutoLoginRequest(serializers.Serializer):
    userId = serializers.IntegerField(validators=[exist_user_id])
