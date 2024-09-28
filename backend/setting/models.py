from django.db import models
from user.models import User
from django.utils import timezone

# Create your models here.
class Datasource(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="主键id")
    datasource_name = models.CharField(max_length=255,unique=True,verbose_name="数据源名称")
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

class TableInfo(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="主键id")
    name = models.CharField(max_length=255,verbose_name="表名")
    ddl = models.TextField(verbose_name="表结构")
    summary = models.TextField(verbose_name="表描述")
    datasource_id = models.ForeignKey(Datasource, on_delete=models.CASCADE,db_column="datasource_id",verbose_name="数据源")
    
    class Meta:
        db_table = "table_info"
        unique_together = ['name', 'datasource_id']

class Model(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="主键id")
    name = models.CharField(max_length=255,verbose_name="模型名称")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,db_column="created_by",verbose_name="创建人")
    model_name = models.CharField(max_length=255,verbose_name="模型名称")
    provider = models.CharField(max_length=255,verbose_name="提供商")
    api_key = models.CharField(max_length=102400,verbose_name="api key")
    base_url = models.URLField(null=True,blank=True,verbose_name="base url")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "model"
        unique_together = ['name', 'created_by']


class SettingType(models.IntegerChoices):
    """系统设置类型"""

    RSA = 0, "私钥秘钥"

class SystemSetting(models.Model):
    """
     系统设置
    """
    type = models.IntegerField(primary_key=True, verbose_name='设置类型', choices=SettingType.choices)
    meta = models.JSONField(verbose_name="配置数据", default=dict)

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True)


    class Meta:
        db_table = "system_setting"
