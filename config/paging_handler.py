from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import serializers


class PagingSerializer(serializers.Serializer):
    totalDataSize = serializers.IntegerField()
    totalPage = serializers.IntegerField()
    hasNext = serializers.BooleanField()
    hasPrevious = serializers.BooleanField()
    currentPage = serializers.IntegerField()
    dataSize = serializers.IntegerField()


def get_paging_data(page: int, pageSize: int, object_list, data_name="data"):

    paginator = Paginator(object_list, pageSize)
    try:
        data_list = paginator.page(page)
    except PageNotAnInteger:
        data_list = paginator.page(1)
    except EmptyPage:
        lastPage = paginator.num_pages
        data_list = paginator.page(lastPage)

    return {
        data_name: data_list,
        "totalDataSize": paginator.count,
        "totalPage": paginator.num_pages,
        "hasNext": data_list.has_next(),
        "hasPrevious": data_list.has_previous(),
        "currentPage": data_list.number,
        "dataSize": len(data_list)
    }
