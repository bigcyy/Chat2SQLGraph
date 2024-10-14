from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ValidationError, ErrorDetail
from common.response import result
from common.exceptions.exception import AppApiException
from common.pipeline.response_util import to_stream_chunk_response, Status

def validation_error_to_result(exc: ValidationError):
    """
    校验异常转响应对象
    :param exc: 校验异常
    :return: 接口响应对象
    """
    try:
        v = find_err_detail(exc.detail)
        if v is None:
            return result.error(str(exc.detail))
        return result.error(str(v))
    except Exception as e:
        return result.error(str(exc.detail))


def find_err_detail(exc_detail):
    if isinstance(exc_detail, ErrorDetail):
        return exc_detail
    if isinstance(exc_detail, dict):
        keys = exc_detail.keys()
        for key in keys:
            _value = exc_detail[key]
            if isinstance(_value, list):
                return find_err_detail(_value)
            if isinstance(_value, ErrorDetail):
                return _value
            if isinstance(_value, dict) and len(_value.keys()) > 0:
                return find_err_detail(_value)
    if isinstance(exc_detail, list):
        for v in exc_detail:
            r = find_err_detail(v)
            if r is not None:
                return r


def handle_exception(exc, context):
    exception_class = exc.__class__
    # 先调用REST framework默认的异常处理方法获得标准错误响应对象
    response = exception_handler(exc, context)
    # 在此处补充自定义的异常处理
    if issubclass(exception_class, ValidationError):
        return validation_error_to_result(exc)
    if issubclass(exception_class, AppApiException):
        return result.Result(exc.code, exc.message, response_status=exc.status_code)
    if issubclass(exception_class, APIException):
        return result.error(exc.detail)
    if response is None:
        return result.error(str(exc))
    return response

def handle_pipeline_exception(exc, chat_id, step_id):
    exception_class = exc.__class__
    if issubclass(exception_class, ValidationError):
        return to_stream_chunk_response(chat_id, step_id, f"参数错误:{str(exc)}", Status.ERROR)
    return to_stream_chunk_response(chat_id, step_id, f"系统错误:{str(exc)}", Status.ERROR)
