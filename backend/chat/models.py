from django.db import models
from setting.models.datasource import Datasource
import uuid
from user.models import User

# Create your models here.

class ChatInfo(models.Model):
    id = models.UUIDField(verbose_name="会话 id",max_length=32,primary_key=True,default=uuid.uuid1)
    datasource_id = models.ForeignKey(Datasource,verbose_name="数据源 id",on_delete=models.CASCADE,db_column="datasource_id")
    user_id = models.ForeignKey(User,verbose_name="用户 id",on_delete=models.CASCADE,db_column="user_id")
    user_demand = models.TextField(blank = True, null = True, verbose_name = "用户需求")
    chat_content = models.JSONField (verbose_name="会话内容",blank = True, null = True)
    sse_message_list = models.JSONField(verbose_name="sse 消息列表",blank = True, null = True)

    created_at = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="更新时间",auto_now=True)

    class Meta:
        db_table = "chat_info"
        verbose_name = "会话信息"
        verbose_name_plural = "会话信息"
