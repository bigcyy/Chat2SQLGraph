from rest_framework import serializers
from .models import Datasource,Model,TableInfo
from user.models import User
from common.response.field_response import ErrMessage
from common.exceptions.exception import ExceptionCodeConstants
from django.db.models import Q,QuerySet
from common.providers.model_provider_constants import ModelProviderConstants
from langchain.chat_models.base import BaseChatModel
import pymysql
from common.utils import rsa_util

class DatasourceSerializer(serializers.ModelSerializer):

    class Create(serializers.ModelSerializer):
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        datasource_name = serializers.CharField(required=True,error_messages=ErrMessage.char("数据源名称"),max_length=20,min_length=1)
        datasource_description = serializers.CharField(required=False,error_messages=ErrMessage.char("数据源描述"),max_length=1024,min_length=0)
        database_name = serializers.CharField(required=True,error_messages=ErrMessage.char("数据库名称"),max_length=20,min_length=1)
        url = serializers.CharField(required=True,error_messages=ErrMessage.char("数据库地址"))
        port = serializers.IntegerField(required=True,error_messages=ErrMessage.char("端口"))
        username = serializers.CharField(required=False,error_messages=ErrMessage.char("用户名"),max_length=255,min_length=0)
        password = serializers.CharField(required=False,error_messages=ErrMessage.char("密码"),max_length=255,min_length=0)

        class Meta:
            model = Datasource
            fields = ['user_id','datasource_name','datasource_description','database_name','url','port','username','password']

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 数据源名称是否存在
            datasource = Datasource.objects.filter(
                datasource_name=self.validated_data.get("datasource_name"),
                created_by=self.validated_data.get("user_id")
            ).first()
            if datasource is not None:
                raise ExceptionCodeConstants.DATASOURCE_NAME_IS_EXIST.value.to_app_api_exception()
            
            # 数据源是否可连接
            try:
                with pymysql.connect(
                    host=self.validated_data.get("url"),
                    port=self.validated_data.get("port"),
                    user=self.validated_data.get("username"),
                    password=self.validated_data.get("password"),
                    database=self.validated_data.get("database_name"),
                    connect_timeout=5
                ) as connection:
                    connection.ping(reconnect=True)
            except pymysql.Error as e:
                raise ExceptionCodeConstants.DATASOURCE_CONNECT_FAILED.value.to_app_api_exception()
        def save_datasource(self):
            self.is_valid(raise_exception=True)
            user= User(id = self.data.get("user_id"))
            m = Datasource(
                **{'datasource_name': self.data.get("datasource_name"),
                'datasource_description': self.data.get("datasource_description"),
                'database_name': self.data.get("database_name"),
                'url': rsa_util.encrypt(self.data.get("url")),
                'port': self.data.get("port"),
                'username': self.data.get("username"),
                'password': rsa_util.encrypt(self.data.get("password")),
                'created_by': user
                })
            m.save()
            return m.id
    
    class Delete(serializers.ModelSerializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))  
        class Meta:
            model = Datasource
            fields = ['datasource_id','user_id']
        def delete_datasource(self):
            self.is_valid(raise_exception=True)
            Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).delete()

    class Query(serializers.ModelSerializer):
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = Datasource
            fields = ['user_id']
        def query_datasource(self):
            self.is_valid(raise_exception=True)
            datasources = Datasource.objects.filter(created_by=self.data.get("user_id")).all()
            return [self.to_dict(datasource) for datasource in datasources]
        
        def to_dict(self,datasource):
            return {
                'id': datasource.id,
                'datasource_name': datasource.datasource_name,
                'datasource_description': datasource.datasource_description,
                'database_name': datasource.database_name,
                'url': rsa_util.decrypt(datasource.url),
                'port': datasource.port,
                'username': datasource.username,
                'password': rsa_util.decrypt(datasource.password),
                'created_by': datasource.created_by.id,
                'created_at': datasource.created_at,
            }
    
class TableInfoSerializer(serializers.ModelSerializer):
    class Create(serializers.ModelSerializer):
        model_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("模型 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        name = serializers.CharField(required=True,error_messages=ErrMessage.char("表名称"),max_length=20,min_length=1)
        ddl = serializers.CharField(required=True,error_messages=ErrMessage.char("表结构"))
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))

        class Meta:
            model = TableInfo
            fields = ['user_id','name','ddl','datasource_id','model_id']
    
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 表是否存在
            table = QuerySet(TableInfo).filter(Q(name=self.data.get("name"))).first()
            if table is not None:
                raise ExceptionCodeConstants.TABLE_NAME_IS_EXIST.value.to_app_api_exception()
            # 是否存在此数据库
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            # 模型是否存在
            model = Model.objects.filter(id=self.data.get("model_id"),created_by=self.data.get("user_id")).first()
            if model is None:
                raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()
            
            # 检查表是否存在于数据源中
            try:
                with pymysql.connect(host=rsa_util.decrypt(datasource.url), port=datasource.port, user=datasource.username, password=rsa_util.decrypt(datasource.password) , database=datasource.database_name) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(f"SHOW TABLES LIKE '{self.data.get('name')}'")
                        result = cursor.fetchone()
                        if not result:
                            raise ExceptionCodeConstants.TABLE_NOT_EXIST.value.to_app_api_exception()
            except pymysql.Error:
                raise ExceptionCodeConstants.DATASOURCE_CONNECT_FAILED.value.to_app_api_exception()

        def save_table_info(self):
            self.is_valid(raise_exception=True)
            # 调用 LLM 总结摘要
            model = self.get_model()

            message = model.invoke(self.get_prompt(self.data.get("ddl")))

            datasource = Datasource(id=self.data.get("datasource_id"))
            # 保存表
            m = TableInfo(
                **{'name': self.data.get("name"),
                'ddl': self.data.get("ddl"),
                'datasource_id': datasource,
                'summary': message.content
                })
            m.save()
            return m.id
        
        def get_model(self) -> BaseChatModel:
            model_config = Model.objects.get(id = self.data.get("model_id"), created_by=self.data.get("user_id"))
            model_provider = ModelProviderConstants.openai_model_provider.value
            model = model_provider.get_model(model_config.model_name, rsa_util.decrypt(model_config.api_key), model_config.base_url)
            return model
        
        def get_prompt(self,ddl:str):
            return f"""
    ## 角色

    你是一个精通 SQL 的开发者，你能够根据表的 DDL 语句生成一个简洁的摘要。

    ## 任务

    根据 DDL 语句生成一段简洁的摘要。尽量用一句话描述这张表，主要的作用，包含的字段信息。不要有太多的结构化数据。

    ## 输入

    {ddl}

    ## 输出

    <summary>${{简洁的摘要}}</summary>
    """
    
    class Delete(serializers.ModelSerializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        table_info_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("表 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = TableInfo
            fields = ['datasource_id','table_info_id','user_id']
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
        
        def delete_table_info(self):
            self.is_valid(raise_exception=True)
            TableInfo.objects.filter(id=self.data.get("table_info_id"),datasource_id=self.data.get("datasource_id")).delete()
    
    class Query(serializers.ModelSerializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = TableInfo
            fields = ['datasource_id','user_id']
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception = True)
            # 数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
        
        def query_table_info(self):
            self.is_valid(raise_exception=True)
            table_infos = TableInfo.objects.filter(datasource_id=self.data.get("datasource_id")).all()
            return [self.to_dict(table_info) for table_info in table_infos]
        
        def to_dict(self,table_info):
            return {
                'id': table_info.id,
                'name': table_info.name,
                'ddl': table_info.ddl,
                'summary': table_info.summary,
                'datasource_id': table_info.datasource_id.id,
            }
        
class ModelSerializer(serializers.ModelSerializer):
    class Query(serializers.ModelSerializer):
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        name = serializers.CharField(required=False, max_length=20,
                                     error_messages=ErrMessage.char("模型名称"))

        model_name = serializers.CharField(required=False, error_messages=ErrMessage.char("基础模型"),max_length=40)

        provider = serializers.CharField(required=False, error_messages=ErrMessage.char("供应商"),max_length=50)

        class Meta:
            model = Model
            fields = ['user_id','name', 'model_name', 'provider']
        def list(self,with_valid=False):
            if with_valid:
                print(self.initial_data)
                super().is_valid(raise_exception=True)

            query_params = {}
            if self.data.get('name') is not None:
                query_params['name__contains'] = self.data.get('name')
            if self.data.get('model_name') is not None:
                query_params['model_name'] = self.data.get('model_name')
            if self.data.get('provider') is not None:
                query_params['provider'] = self.data.get('provider')
            
            query_params['created_by'] = self.data.get("user_id")

            models = Model.objects.filter(**query_params).order_by('-created_at').all()

            
            return [self.to_dict(model) for model in models]
        
        def to_dict(self,model):
            return {
                'id': model.id,
                'name': model.name,
                'model_name': model.model_name,
                'api_key': rsa_util.decrypt(model.api_key),
                'base_url': model.base_url,
                'provider': model.provider,
                'created_at': model.created_at,
            }
    class Create(serializers.ModelSerializer):

        name = serializers.CharField(required=True,error_messages=ErrMessage.char("模型别名"),max_length=20,min_length=1)
        model_name = serializers.CharField(required=True,error_messages=ErrMessage.char("模型名称"),max_length=40,min_length=1)
        provider = serializers.CharField(required=True,error_messages=ErrMessage.char("提供商"),max_length=50,min_length=1)
        api_key = serializers.CharField(required=True,error_messages=ErrMessage.char("api_key"),max_length=255,min_length=1)
        base_url = serializers.CharField(required=False,error_messages=ErrMessage.char("base_url"),max_length=255,min_length=0)
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = Model
            fields = ['name','model_name','provider','api_key','base_url','user_id']

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 查看模型提供商是否存在
            try:
                model_provider = ModelProviderConstants[self.data.get("provider")].value
            except KeyError:
                raise ExceptionCodeConstants.MODEL_PROVIDER_NOT_EXIST.value.to_app_api_exception()
    
            is_valid = model_provider.model_is_valid(self.data.get("model_name"),self.data.get("api_key"),self.data.get("base_url"))
            if not is_valid:
                raise ExceptionCodeConstants.MODEL_IS_NOT_VALID.value.to_app_api_exception()
            
            # 查看别名是否已经在数据库中存在
            model = Model.objects.filter(name=self.data.get("name")).first()
            if model is not None:
                raise ExceptionCodeConstants.MODEL_NICKNAME_IS_EXIST.value.to_app_api_exception()


        def save_model(self) -> int:
            self.is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            user = User(id=user_id)
            # 保存模型
            m = Model(
                **{'name': self.data.get("name"),
                'model_name': self.data.get("model_name"),
                'provider': self.data.get("provider"),
                'api_key': rsa_util.encrypt(self.data.get("api_key")),
                'base_url': self.data.get("base_url"),
                'created_by': user
                }
            )
            m.save()    
            return m.id
    class Delete(serializers.ModelSerializer):
        model_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("模型 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = Model
            fields = ['model_id','user_id']
        def delete_model(self):
            self.is_valid(raise_exception=True)
            Model.objects.filter(id=self.data.get("model_id"),created_by=self.data.get("user_id")).delete()
    
    
    
    


