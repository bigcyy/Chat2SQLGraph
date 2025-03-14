from rest_framework import serializers
from .models.datasource import Datasource
from .models.model import Model
from .models.table_info import TableInfo
from user.models import User
from common.response.field_response import ErrMessage
from common.exceptions.exception import ExceptionCodeConstants
from django.db.models import Q,QuerySet
from common.providers.model_provider_constants import ModelProviderConstants
from langchain.chat_models.base import BaseChatModel
import pymysql
from common.utils import rsa_util
import threading

class DatasourceSerializer(serializers.ModelSerializer):

    class AddDatasource(serializers.ModelSerializer):
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
        def add_datasource(self):
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
            return self.to_dict(m)
        
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
    class DeleteDatasource(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))  
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()

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
        table_name_list = serializers.ListField(required=True,error_messages=ErrMessage.char("表名称列表"))
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))

        class Meta:
            model = TableInfo
            fields = ['user_id','table_name_list','datasource_id','model_id']
    
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 是否存在此数据库
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            # 表是否存在
            for table_name in self.data.get("table_name_list"):
                table = TableInfo.objects.filter(name=table_name,datasource_id=self.data.get("datasource_id")).first()
                if table is not None:
                    raise ExceptionCodeConstants.TABLE_NAME_IS_EXIST.value.to_app_api_exception()
            # 模型是否存在
            model = Model.objects.filter(id=self.data.get("model_id"),created_by=self.data.get("user_id")).first()
            if model is None:
                raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()
            
            # 检查表是否存在于数据源中
            try:
                with pymysql.connect(host=rsa_util.decrypt(datasource.url), port=datasource.port, user=datasource.username, password=rsa_util.decrypt(datasource.password) , database=datasource.database_name) as connection:
                    with connection.cursor() as cursor:
                        for table_name in self.data.get("table_name_list"):
                            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
                            result = cursor.fetchone()
                            if not result:
                                raise ExceptionCodeConstants.TABLE_NOT_EXIST.value.to_app_api_exception()
                        
            except pymysql.Error:
                raise ExceptionCodeConstants.DATASOURCE_CONNECT_FAILED.value.to_app_api_exception()

        def save_table_info(self):
            self.is_valid(raise_exception=True)
            datasource = Datasource.objects.get(id=self.data.get("datasource_id"))
            # 获取表的 DDL
            ddl_list = []
            try:
                with pymysql.connect(host=rsa_util.decrypt(datasource.url), port=datasource.port, user=datasource.username, password=rsa_util.decrypt(datasource.password) , database=datasource.database_name) as connection:
                    with connection.cursor() as cursor:
                        for table_name in self.data.get("table_name_list"):
                            cursor.execute("SHOW CREATE TABLE %s"%table_name)
                            ddl = cursor.fetchone()
                            ddl_list.append(ddl[1])
            except pymysql.Error:
                raise ExceptionCodeConstants.DATASOURCE_CONNECT_FAILED.value.to_app_api_exception()
            # 调用 LLM 总结摘要
            model = self.get_model()
            summary_list = []
            for ddl in ddl_list:
                message = model.invoke(self.get_prompt(ddl))
                summary_list.append(message.content)
            datasource = Datasource(id=self.data.get("datasource_id"))
            # 保存表
            for i in range(len(self.data.get("table_name_list"))):
                m = TableInfo(
                    **{'name': self.data.get("table_name_list")[i],
                    'ddl': ddl_list[i],
                    'datasource_id': datasource,
                    'summary': summary_list[i]
                })
                m.save()
            return m.id
        def multi_thread_save(self):
            self.is_valid(raise_exception=True)
            datasource = Datasource.objects.get(id=self.data.get("datasource_id"))
        
            def multi_thread_get_table_ddl_and_summary(datasource,table_name):
                try:
                    with pymysql.connect(host=rsa_util.decrypt(datasource.url), port=datasource.port, user=datasource.username, password=rsa_util.decrypt(datasource.password) , database=datasource.database_name) as connection:
                        with connection.cursor() as cursor:
                            # todo sql 注入风险
                            cursor.execute("SHOW CREATE TABLE %s"%table_name)
                            ddl = cursor.fetchone()[1]
                            summary = multi_thread_get_summary(table_name,ddl)
                except pymysql.Error as e:
                    raise ExceptionCodeConstants.DATASOURCE_CONNECT_FAILED.value.to_app_api_exception()
                return {
                    "table_name": table_name,
                    "ddl": ddl,
                    "summary": summary
                }

            def multi_thread_get_summary(table_name:str,ddl:str):
                model = self.get_model()
                message = model.invoke(self.get_prompt(ddl))
                return {
                    "table_name": table_name,
                    "summary": message.content
                }

            threads = []
            results = []
            for table_name in self.data.get("table_name_list"):
                thread = threading.Thread(target=lambda tn=table_name: results.append(multi_thread_get_table_ddl_and_summary(datasource, tn)))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Save table info
            table_info_objects = [
                TableInfo(
                    name=result["table_name"],
                    ddl=result["ddl"],
                    datasource_id=datasource,
                    summary=result["summary"]
                ) for result in results
            ]
            TableInfo.objects.bulk_create(table_info_objects)
        def get_model(self) -> BaseChatModel:
            model_config = Model.objects.get(id = self.data.get("model_id"), created_by=self.data.get("user_id"))
            model_provider = ModelProviderConstants[model_config.provider].value
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
    
    class DeleteTable(serializers.ModelSerializer):
        table_info_ids = serializers.ListField(required=True,error_messages=ErrMessage.char("表 id 列表"))
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = TableInfo
            fields = ['datasource_id','table_info_ids','user_id']
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            
        def delete_table_info(self):
            self.is_valid(raise_exception=True)
            # 查询出要删除的对象
            table_infos = TableInfo.objects.filter(
                id__in=self.data.get("table_info_ids"),
                datasource_id=self.data.get("datasource_id")
            )
            # 将 id转为 set
            existing_ids = set(table_infos.values_list('id', flat=True))
            success_ids = []
            error_ids = []
            
            # 依次删除每个对象
            for table_info in table_infos:
                id = table_info.id
                try:
                    table_info.delete()
                    success_ids.append(id)
                except Exception as e:
                    error_ids.append(id)
        
            not_exist_ids = set(self.data.get("table_info_ids")) - existing_ids
        
            return {
                "success_ids": success_ids,
                "not_exist_ids": list(not_exist_ids),
                "error_ids": error_ids
            }
    
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
    class Add(serializers.ModelSerializer):

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
            model = Model.objects.filter(name=self.data.get("name"),created_by=self.data.get("user_id")).first()
            if model is not None:
                raise ExceptionCodeConstants.MODEL_NICKNAME_IS_EXIST.value.to_app_api_exception()


        def add_model(self) -> int:
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
            return self.to_dict(m)
        
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
    class Remove(serializers.ModelSerializer):
        model_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("模型 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = Model
            fields = ['model_id','user_id']
        def delete_model(self):
            self.is_valid(raise_exception=True)
            Model.objects.filter(id=self.data.get("model_id"),created_by=self.data.get("user_id")).delete()
    class Test(serializers.Serializer):
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        provider = serializers.CharField(required=True,error_messages=ErrMessage.char("提供商"),max_length=50,min_length=1)
        model_name = serializers.CharField(required=True,error_messages=ErrMessage.char("模型名称"),max_length=40,min_length=1)
        api_key = serializers.CharField(required=True,error_messages=ErrMessage.char("api_key"),max_length=255,min_length=1)
        base_url = serializers.CharField(required=False,error_messages=ErrMessage.char("base_url"),max_length=255,min_length=0)
        
        def test_model(self):
            self.is_valid(raise_exception=True)
            model_provider = ModelProviderConstants[self.data.get("provider")].value
            model = model_provider.get_model(self.data.get("model_name"),self.data.get("api_key"),self.data.get("base_url"))
            return model.test_invoke()

class RemoteTableInfoSerializer(serializers.ModelSerializer):
    class Query(serializers.ModelSerializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("创建人"))
        class Meta:
            model = TableInfo
            fields = ['datasource_id','user_id']
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()

        def query_table_info(self):
            self.is_valid(raise_exception=True)
            # 获取数据源
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            # 连接数据库
            try:
                with pymysql.connect(host=rsa_util.decrypt(datasource.url), port=datasource.port, user=datasource.username, password=rsa_util.decrypt(datasource.password) , database=datasource.database_name) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
            except pymysql.Error:
                raise ExceptionCodeConstants.DATASOURCE_CONNECT_FAILED.value.to_app_api_exception()

            return tables
    
    
    


