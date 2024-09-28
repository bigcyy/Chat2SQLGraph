from enum import Enum
from rest_framework import status


class AppApiException(Exception):
    """
    项目内异常
    """
    status_code = status.HTTP_200_OK

    def __init__(self, code, message):
        self.code = code
        self.message = message


class AppAuthenticationFailed(AppApiException):
    """
    未认证(未登录)异常
    """
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, code = 4001, message = "未认证(未登录)，请先登录"):
        self.code = code
        self.message = message


class AppUnauthorizedFailed(AppApiException):
    """
    未授权(没有权限)异常
    """
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, code = 4002, message = "未授权(没有权限)"):
        self.code = code
        self.message = message


class ExceptionCodeConstantsValue:
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def get_message(self):
        return self.message

    def get_code(self):
        return self.code

    def to_app_api_exception(self):
        return AppApiException(code=self.code, message=self.message)


class ExceptionCodeConstants(Enum):
    INCORRECT_USERNAME_AND_PASSWORD = ExceptionCodeConstantsValue(1000, "用户名或者密码不正确")
    NOT_AUTHENTICATION = ExceptionCodeConstantsValue(1001, "请先登录,并携带用户Token")
    EMAIL_SEND_ERROR = ExceptionCodeConstantsValue(1002, "邮件发送失败")
    EMAIL_FORMAT_ERROR = ExceptionCodeConstantsValue(1003, "邮箱格式错误")
    EMAIL_IS_EXIST = ExceptionCodeConstantsValue(1004, "邮箱已经被注册,请勿重复注册")
    EMAIL_IS_NOT_EXIST = ExceptionCodeConstantsValue(1005, "邮箱尚未注册,请先注册")
    CODE_ERROR = ExceptionCodeConstantsValue(1005, "验证码不正确,或者验证码过期")
    USERNAME_IS_EXIST = ExceptionCodeConstantsValue(1006, "用户名已被使用,请使用其他用户名")
    USERNAME_ERROR = ExceptionCodeConstantsValue(1006, "用户名不能为空,并且长度在6-20")
    PASSWORD_NOT_EQ_RE_PASSWORD = ExceptionCodeConstantsValue(1007, "密码与确认密码不一致")
    USER_IS_NOT_ACTIVE = ExceptionCodeConstantsValue(1008, "用户已被禁用,请联系管理员!")
    DATASOURCE_NAME_IS_EXIST = ExceptionCodeConstantsValue(1009, "数据源名称已存在")
    MODEL_PROVIDER_NOT_EXIST = ExceptionCodeConstantsValue(1010, "模型提供商不存在")
    MODEL_NAME_NOT_EXIST = ExceptionCodeConstantsValue(1011, "模型名称不存在")
    MODEL_TEST_FAILED = ExceptionCodeConstantsValue(1012, "模型测试失败")
    MODEL_NICKNAME_IS_EXIST = ExceptionCodeConstantsValue(1013, "名称已存在")
    MODEL_IS_NOT_VALID = ExceptionCodeConstantsValue(1014, "模型信息不合法")
    DATASOURCE_NOT_EXIST = ExceptionCodeConstantsValue(1015, "数据源不存在")
    MODEL_NOT_EXIST = ExceptionCodeConstantsValue(1016, "模型不存在")
    TABLE_NOT_EXIST = ExceptionCodeConstantsValue(1017, "表不存在")
    CHAT_NOT_EXIST = ExceptionCodeConstantsValue(1018, "聊天不存在")
    DATASOURCE_CONNECT_FAILED = ExceptionCodeConstantsValue(1019, "数据源连接失败")
