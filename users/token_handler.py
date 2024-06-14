import datetime

import jwt
from pytz import timezone
from rest_framework import status
from rest_framework.request import Request

from config.basemodel import ApiResponse
from config.settings import JWT_SECRET, REQUEST_BODY, REQUEST_QUERY, REQUEST_PATH
from users.models import User
from users.token_serializer import TokenSerializer


def token_permission_validator(where_is_userId: str = REQUEST_PATH, userIdName: str = 'userId'):
    """
    :param where_is_userId: userId가 어디에 있는지 명세
    :param userIdName: userId가 어떤 이름으로 들어있는지 명세
    """

    def decorator(fuc):
        def decorated_func(self, request: Request, *args, **kwargs):

            # header에 AccessToken이 있는지 확인
            if 'AccessToken' not in request.headers:
                return ApiResponse.on_fail(
                    "AccessToken를 입력하세요"
                )

            # AccessToken 이 유효한지 확인
            is_valid, message, decoded_access_token = decode_token(request.headers.get('AccessToken'))

            # 만료 되거나 decoding 이 안되는 유효하지 않은 토큰이라면 실패 응답 반환
            if not is_valid:
                return ApiResponse.on_fail(
                    message,
                    response_status=status.HTTP_403_FORBIDDEN
                )

            # 토큰의 userId가 유효한지 확인
            userId = None
            if where_is_userId == REQUEST_PATH:
                userId = kwargs.get(userIdName)
            elif where_is_userId == REQUEST_BODY:
                userId = request.data.get(userIdName)
            elif where_is_userId == REQUEST_QUERY:
                userId = request.query_params.get(userIdName)

            # 토큰의 userId와 요청의 userId가 일치하는지 확인
            is_valid, message = validate_user_id_token(decoded_access_token, userId)

            if not is_valid:
                return ApiResponse.on_fail(
                    message,
                    response_status=status.HTTP_403_FORBIDDEN
                )

            return fuc(self, request, *args, **kwargs)

        return decorated_func

    return decorator


def decode_token(token: str):
    is_valid = True
    message = ""
    decoded_token = None
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms='HS256')
    except jwt.ExpiredSignatureError:
        is_valid = False
        message = "토큰이 만료되었습니다."
    except jwt.InvalidTokenError:
        is_valid = False
        message = "잘못된 토큰입니다."

    if not is_valid:
        return is_valid, message, decoded_token

    return is_valid, message, decoded_token


def create_token(userId: int = None) -> TokenSerializer:
    if not userId:
        raise ValueError("userId 가 없습니다.")

    return TokenSerializer.to_validated_serializer(
        access_token=create_access_token(userId=userId),
        refresh_token=create_refresh_token(userId=userId)
    )


def create_access_token(userId: int = None):
    return jwt.encode(
        {
            'userId': str(userId),
            # 2시간
            'exp': datetime.datetime.now(timezone('Asia/Seoul')) + datetime.timedelta(hours=2)
        }, JWT_SECRET, algorithm='HS256'
    )


def create_refresh_token(userId: int = None):
    return jwt.encode(
        {
            'userId': str(userId),
            # 1 week
            'exp': datetime.datetime.now(timezone('Asia/Seoul')) + datetime.timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256'
    )


def validate_user_id_token(decoded_token: dict, userId: int = None):
    is_valid = True
    message = ""
    if not userId:
        is_valid = False
        message = "userId 가 없습니다."

    if userId != int(decoded_token['userId']):
        is_valid = False
        message = "userId가 유효 하지 않은 토큰입니다."

    return is_valid, message


def auto_login(userId: int, token: TokenSerializer):
    access_token = token.data.get('AccessToken')
    refresh_token = token.data.get('RefreshToken')

    # AccessToken 이 유효한지 확인
    is_valid, message, decoded_access_token = decode_token(access_token)
    if not is_valid:
        return is_valid, "<AccessToken> " + message, None

    # RefreshToken 이 토큰이 유효한지 확인
    is_valid, message, decoded_refresh_token = decode_token(refresh_token)
    if not is_valid:
        return is_valid, "<RefreshToken> " + message, None

    # 토큰의 AccessToken의  userId가 유효한지 확인
    is_valid, message = validate_user_id_token(decoded_access_token, userId)
    if not is_valid:
        return is_valid, "AccessToken 안 " + message, None

    # 토큰의 RefreshToken 의  userId가 유효한지 확인
    is_valid, message = validate_user_id_token(decoded_refresh_token, userId)
    if not is_valid:
        return is_valid, "RefreshToken" + message, None

    # 토큰의 RefreshToken이 user.refresh_token과 일치하는지 확인
    is_valid = User.objects.get(id=userId).refresh_token == refresh_token
    if not is_valid:
        return is_valid, "데이터 베이스의 Refresh 토큰이 유효하지 않습니다.", None

    # AccessToken의 만료 시간이 30분 이내라면 AccessToken을 재발급
    token_expired_time = datetime.datetime.fromtimestamp(decoded_access_token['exp'], timezone('Asia/Seoul'))
    now_time = datetime.datetime.now(timezone('Asia/Seoul'))
    if (token_expired_time - now_time).seconds < 30 * 60:
        print("재발급")
        access_token = create_access_token(userId)

    token = TokenSerializer.to_validated_serializer(
        access_token=access_token,
        refresh_token=refresh_token
    )

    return is_valid, message, token
