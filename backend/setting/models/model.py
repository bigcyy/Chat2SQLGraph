from django.db import models
from user.models import User

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