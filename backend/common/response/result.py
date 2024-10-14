from typing import List

from django.http import JsonResponse
from rest_framework import status


class Page(dict):
    """
    分页对象
    """

    def __init__(self, total: int, records: List, current_page: int, page_size: int, **kwargs):
        super().__init__(**{'total': total, 'records': records, 'current': current_page, 'size': page_size})


class Result(JsonResponse):
    charset = 'utf-8'
    """
     接口统一返回对象
    """

    def __init__(self, code=200, message="成功", data=None, response_status=status.HTTP_200_OK, **kwargs):
        back_info_dict = {"code": code, "message": message, 'data': data}
        super().__init__(data=back_info_dict, status=response_status, **kwargs)

def success(data=None, message="成功", **kwargs):
    """
    获取一个成功的响应对象
    :param data: 接口响应数据（可选）
    :param message: 成功提示（默认为"成功"）
    :param kwargs: 其他可选参数
    :return: 请求响应对象
    """
    return Result(data=data, message=message, **kwargs)

def error(message):
    """
    获取一个失败的响应对象
    :param message: 错误提示
    :return: 接口响应对象
    """
    return Result(code=500, message=message)
