from rest_framework.serializers import ValidationError


def less_than(maxv):
    def inner_fun(value):
        if value < maxv:
            return value

        raise ValidationError(f'{maxv} 보다 작아야 합니다.')

    return inner_fun
