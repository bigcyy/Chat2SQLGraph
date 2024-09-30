from django.db import models
from common.utils import rsa_util

class User(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="主键id")
    nickname = models.CharField(max_length=150, verbose_name="昵称", default="")
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=102400, verbose_name="密码")
    role = models.CharField(max_length=150, verbose_name="角色")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, null=True)

    class Meta:
        db_table = "user"

    def set_password(self, raw_password):
        self.password = rsa_util.encrypt(raw_password)
        self._password = raw_password

