from rest_framework import serializers, status


class ImageRequest(serializers.Serializer):
    image = serializers.ImageField()

    def is_valid(self, *, raise_exception=False):
        super_valid = super().is_valid()
        if not super_valid:
            return False, status.HTTP_400_BAD_REQUEST

        return True, status.HTTP_200_OK

