from django.db import models
from setting.models.datasource import Datasource

class TableInfo(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="主键id")
    name = models.CharField(max_length=255,verbose_name="表名")
    ddl = models.TextField(verbose_name="表结构")
    summary = models.TextField(verbose_name="表描述")
    datasource_id = models.ForeignKey(Datasource, on_delete=models.CASCADE,db_column="datasource_id",verbose_name="数据源")
    
    class Meta:
        db_table = "table_info"
        unique_together = ['name', 'datasource_id']
