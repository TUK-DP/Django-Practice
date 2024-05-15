from rest_framework import serializers, status


def positive_validator(value):
    if value < 0:
        raise serializers.ValidationError(f'{value} 이 음수입니다.')


class GetAroundCenterRequest(serializers.Serializer):
    # 위도
    lat = serializers.FloatField(help_text='사용자 위도')
    # 경도
    lon = serializers.FloatField(help_text='사용자 경도')
    # 반경 (km)
    radius = serializers.FloatField(help_text='반경 (km) 거리안 치매센터 조회', validators=[positive_validator])


class CenterResponse(serializers.Serializer):
    치매센터명 = serializers.CharField()
    치매센터유형 = serializers.CharField()
    소재지도로명주소 = serializers.CharField()
    소재지지번주소 = serializers.CharField()
    위도 = serializers.CharField()
    경도 = serializers.CharField()
    설립연월 = serializers.CharField()
    건축물면적 = serializers.CharField()
    부대시설정보 = serializers.CharField()
    의사인원수 = serializers.CharField()
    간호사인원수 = serializers.CharField()
    사회복지사인원수 = serializers.CharField()
    기타인원현황 = serializers.CharField()
    운영기관명 = serializers.CharField()
    운영기관대표자명 = serializers.CharField()
    운영기관전화번호 = serializers.CharField()
    운영위탁일자 = serializers.CharField()
    주요치매관리프로그램소개 = serializers.CharField()
    관리기관전화번호 = serializers.CharField()
    관리기관명 = serializers.CharField()
    데이터기준일자 = serializers.CharField()
    제공기관코드 = serializers.CharField()
    제공기관명 = serializers.CharField()
    나와의거리 = serializers.FloatField()
