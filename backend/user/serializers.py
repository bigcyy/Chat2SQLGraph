from rest_framework import serializers
from user.models import User
from user.utils import password_encrypt
from django.db.models import Q, QuerySet
from common.exceptions.exception import ExceptionCodeConstants
from common.response.field_response import ErrMessage
from django.core import validators
import re
from common.auth.jwt_utils import generate_jwt_token

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True,
                                     error_messages=ErrMessage.char("用户名"))

    password = serializers.CharField(required=True, error_messages=ErrMessage.char("密码"))

    class Meta:
        model = User
        fields = '__all__'
    
    def is_valid(self, *, raise_exception=False):
        """
        校验参数
        :param raise_exception: 是否抛出异常 只能是True
        :return: 用户信息
        """
        super().is_valid(raise_exception=True)
        username = self.data.get("username")
        password = password_encrypt(self.data.get("password"))
        user = QuerySet(User).filter(Q(username=username,
                                       password=password)).first()
        if user is None:
            raise ExceptionCodeConstants.INCORRECT_USERNAME_AND_PASSWORD.value.to_app_api_exception()
        if not user.is_active:
            raise ExceptionCodeConstants.USER_IS_NOT_ACTIVE.value.to_app_api_exception()
        return user
    
    def get_jwt_token(self) -> str:
        user = self.is_valid(raise_exception=True)
        return generate_jwt_token(user.id)

    class Refresh(serializers.Serializer):
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户id"))
        class Meta:
            model = User
            fields = ['user_id']
        def refresh_jwt_token(self):
            self.is_valid(raise_exception=True)
            return generate_jwt_token(self.data.get("user_id"))

class RegisterSerializer(serializers.Serializer):
    """
    注册请求对象
    """
    nickname = serializers.CharField(required=True,
                                     error_messages=ErrMessage.char("昵称"),
                                     max_length=20,
                                     min_length=1,
                                     )
    username = serializers.CharField(required=True,
                                     error_messages=ErrMessage.char("用户名"),
                                     max_length=20,
                                     min_length=6,
                                     )
    password = serializers.CharField(required=True, error_messages=ErrMessage.char("密码"),
                                     validators=[validators.RegexValidator(regex=re.compile(
                                         "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                         "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                         , message="密码长度6-20个字符，必须字母、数字、特殊字符组合")])

    re_password = serializers.CharField(required=True,
                                        error_messages=ErrMessage.char("确认密码"),
                                        validators=[validators.RegexValidator(regex=re.compile(
                                            "^(?![a-zA-Z]+$)(?![A-Z0-9]+$)(?![A-Z_!@#$%^&*`~.()-+=]+$)(?![a-z0-9]+$)(?![a-z_!@#$%^&*`~()-+=]+$)"
                                            "(?![0-9_!@#$%^&*`~()-+=]+$)[a-zA-Z0-9_!@#$%^&*`~.()-+=]{6,20}$")
                                            , message="确认密码长度6-20个字符，必须字母、数字、特殊字符组合")])


    class Meta:
        model = User
        fields = '__all__'

    # todo: 给方法加锁
    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        # 密码和确认密码是否一致
        if self.data.get('password') != self.data.get('re_password'):
            raise ExceptionCodeConstants.PASSWORD_NOT_EQ_RE_PASSWORD.value.to_app_api_exception()
        # 用户名是否存在
        username = self.data.get("username")
        u = QuerySet(User).filter(Q(username=username)).first()
        if u is not None:
            raise ExceptionCodeConstants.USERNAME_IS_EXIST.value.to_app_api_exception()
        return True
    
    def save_user(self):
        m = User(
            **{'username': self.data.get("username"),
               'role': "user","nickname":self.data.get("nickname")})
        m.set_password(self.data.get("password"))
        # 插入用户
        m.save()
        return m.id

    def get_jwt_token(self):
        # return generate_jwt_token(self.data.get("username"))
        return "123"
