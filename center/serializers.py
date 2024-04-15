from rest_framework import serializers, status


class GetAroundCenterRequest(serializers.Serializer):
    # 위도
    lat = serializers.FloatField(help_text='사용자 위도')
    # 경도
    lon = serializers.FloatField(help_text='사용자 경도')
    # 반경 (km)
    radius = serializers.FloatField(help_text='반경 (km) 거리안 치매센터 조회')

    def is_valid(self, *, raise_exception=False):
        super_valid = super().is_valid()
        # 유효하지 않다면 False, 400 반환
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        # 위도 , 경도가 양수인지 확인
        if self.data['lat'] < 0 or self.data['lon'] < 0:
            self._errors['lat'] = [f'lat: {self.data.get("lat")} 또는 lon: {self.data.get("lon")} 이 음수입니다.']
            return False, status.HTTP_400_BAD_REQUEST

        # 반경이 양수인지 확인
        if self.data['radius'] < 0:
            self._errors['radius'] = [f'radius: {self.data.get("radius")} 이 음수입니다.']
            return False, status.HTTP_400_BAD_REQUEST

        return True, status.HTTP_200_OK
