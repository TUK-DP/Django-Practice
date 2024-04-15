import math

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from center.center_data import centers
from center.serializers import GetAroundCenterRequest
from config.basemodel import ApiResponse


class GetAroundCenter(APIView):
    @transaction.atomic
    @swagger_auto_schema(operation_description="주변 치매 센터 조회", query_serializer=GetAroundCenterRequest,
                         responses={"200": '성공'})
    def get(self, request):
        requestSerial = GetAroundCenterRequest(data=request.query_params)

        isValid, response_status = requestSerial.is_valid()
        # 유효성 검사 통과하지 못한 경우
        if not isValid:
            return ApiResponse.on_fail(requestSerial.errors, response_status=response_status)

        request = requestSerial.validated_data

        # 위도 경도 가져오기
        lat = request.get('lat')
        lon = request.get('lon')
        # 반경 가져오기
        radius = request.get('radius')

        # 반경 내의 치매센터 조회
        filteredCenters = []
        for center in centers["records"]:
            if "+" in center['위도']:
                center['위도'] = center['위도'].split("+")[0]
            if "+" in center['경도']:
                center['경도'] = center['경도'].split("+")[0]

            distance = haversine(lat, lon, float(center['위도']), float(center['경도']))

            if distance <= radius:
                center['나와의거리'] = distance
                filteredCenters.append(center)

        return ApiResponse.on_success(
            result=filteredCenters,
            response_status=status.HTTP_200_OK
        )


def haversine(lat1, lon1, lat2, lon2):
    # 위도와 경도를 라디안 단위로 변환
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 두 지점의 위도와 경도 차이
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # 허버사인 공식 사용
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 지구 반지름 (킬로미터)
    r = 6371

    # 결과 거리 (킬로미터)
    return c * r
