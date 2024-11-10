from django.db import models
from user.models import User
from setting.models.model import Model
from setting.models.datasource import Datasource
from django.contrib.postgres.fields import ArrayField
import uuid
# Create your models here.
class Application(models.Model):
    """
    应用
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=255, verbose_name="应用名称")
    description = models.TextField(null=True, blank=True, verbose_name="应用描述")
    creator = models.ForeignKey(User ,on_delete=models.CASCADE, verbose_name="创建人")
    model = models.ForeignKey(Model, null=True, blank=True, on_delete=models.CASCADE, verbose_name="模型")
    datasource = models.ForeignKey(Datasource, null=True, blank=True, on_delete=models.CASCADE, verbose_name="数据源")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "application"

class ApplicationAccessToken(models.Model):
    """
    应用认证token
    """
    application = models.OneToOneField(Application, primary_key=True, on_delete=models.CASCADE, verbose_name="应用id")
    access_token = models.CharField(max_length=128, verbose_name="用户公开访问 认证token", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="是否开启公开访问")
    access_num = models.IntegerField(default=100, verbose_name="访问次数")
    white_active = models.BooleanField(default=False, verbose_name="是否开启白名单")
    white_list = ArrayField(verbose_name="白名单列表",
                            base_field=models.CharField(max_length=128, blank=True)
                            , default=list)

    class Meta:
        db_table = "application_access_token"

class ApplicationChatInfo(models.Model):
    """
    应用会话信息
    """

    id = models.UUIDField(verbose_name="会话 id",max_length=32,primary_key=True,default=uuid.uuid1)
    user_demand = models.TextField(verbose_name = "用户需求")
    chat_content = models.JSONField (verbose_name="会话内容",blank = True, null = True)
    sse_message_list = models.JSONField(verbose_name="sse 消息列表",blank = True, null = True)
    created_at = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新时间",auto_now=True)

    class Meta:
        db_table = "application_chat_info"

