from django.db import models
from user.models import User
from django.utils import timezone

class Datasource(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="主键id")
    datasource_name = models.CharField(max_length=255,verbose_name="数据源名称")
    datasource_description = models.TextField(max_length=1024,blank=True, null=True,default="",verbose_name="数据源描述")
    database_name = models.CharField(max_length=255,verbose_name="数据库名称")
    url = models.CharField(max_length=102400,verbose_name="数据库地址")
    port = models.IntegerField(verbose_name="端口")
    username = models.CharField(max_length=255, blank=True, null=True,verbose_name="用户名")
    password = models.CharField(max_length=102400, blank=True, null=True,verbose_name="密码")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,db_column="created_by",verbose_name="创建人")
    created_at = models.DateTimeField(default=timezone.now,verbose_name="创建时间")

    class Meta:
        db_table = "datasource"
        unique_together = (("datasource_name", "created_by"))
