from django.db import models

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
