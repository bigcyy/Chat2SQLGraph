from rest_framework import serializers
from common.response.field_response import ErrMessage
from common.exceptions.exception import ExceptionCodeConstants
from setting.models.datasource import Datasource
from setting.models.model import Model
from setting.models.table_info import TableInfo
from application.models import Application, ApplicationAccessToken, ApplicationChatInfo
from user.models import User
from django.http import HttpRequest
import hashlib
import uuid
from common.providers.model_provider_constants import ModelProviderConstants
from common.pipeline.pipeline_manager import PipelineManager
from common.pipeline.steps.table_select import TableSelectStep
from common.pipeline.steps.generate_sql import GenerateSqlStep
from common.pipeline.steps.execute_sql import ExecuteSqlStep
from common.pipeline.steps.data_to_chart import DataToChartStep
from common.utils import rsa_util
from langchain_core.language_models import BaseChatModel
from django.http import StreamingHttpResponse

from common.auth.jwt_utils import generate_jwt_token

class ApplicationSerializer(serializers.Serializer):
    class ApplicationCreate(serializers.Serializer):
        name = serializers.CharField(required=True,min_length=1,max_length=255,error_messages=ErrMessage.char("应用名称"))
        description = serializers.CharField(required=False,allow_blank=True,max_length=1000,error_messages=ErrMessage.char("应用描述"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        model_id = serializers.IntegerField(required=False,error_messages=ErrMessage.char("模型 id"))
        datasource_id = serializers.IntegerField(required=False,error_messages=ErrMessage.char("数据源 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if self.data.get('datasource_id') is not None :
                datasource = Datasource.objects.filter(id=self.data.get('datasource_id'),created_by=self.data.get('user_id')).first()
                if not datasource:
                    raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            if self.data.get('model_id') is not None:
                model = Model.objects.filter(id=self.data.get('model_id'),created_by=self.data.get('user_id')).first()
                if not model:
                    raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()

        def save(self):
            self.is_valid(raise_exception=True)
            creator = User(id=self.data.get('user_id'))
            model = Model(id=self.data.get('model_id')) if self.data.get('model_id') is not None else None
            datasource = Datasource(id=self.data.get('datasource_id')) if self.data.get('datasource_id') is not None else None
            # 创建应用
            application = Application.objects.create(name=self.data['name'],description=self.data.get('description'),creator=creator,model=model,datasource=datasource)
            # 创建应用认证 token
            ApplicationAccessToken.objects.create(application=application,access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24])                                          
            return ApplicationSerializerModel(application).data
    class ApplicationUpdate(serializers.Serializer):
        id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        name = serializers.CharField(required=True,min_length=1,max_length=255,error_messages=ErrMessage.char("应用名称"))
        description = serializers.CharField(required=True,allow_blank=True,allow_null=True,max_length=1000,error_messages=ErrMessage.char("应用描述"))
        model = serializers.IntegerField(required=True,allow_null=True,error_messages=ErrMessage.char("模型 id"))
        datasource = serializers.IntegerField(required=True,allow_null=True,error_messages=ErrMessage.char("数据源 id"))
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            if not application:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()
            if self.data.get('datasource') is not None :
                datasource = Datasource.objects.filter(id=self.data.get('datasource'),created_by=self.data.get('user_id')).first()
                if not datasource:
                    raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            if self.data.get('model') is not None:
                model = Model.objects.filter(id=self.data.get('model'),created_by=self.data.get('user_id')).first()
                if not model:
                    raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()

        def update(self):
            self.is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            application.name = self.data.get('name')
            application.description = self.data.get('description')
            application.model = Model(id=self.data.get('model')) if self.data.get('model') is not None else None
            application.datasource = Datasource(id=self.data.get('datasource')) if self.data.get('datasource') is not None else None
            application.save()
            return ApplicationSerializerModel(application).data
    
    class ApplicationDelete(serializers.Serializer):
        id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            if not application:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()

        def delete(self):
            self.is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            application.delete()
            return True
    
    class ApplicationDetail(serializers.Serializer):
        id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            if not application:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()

        def detail(self):
            self.is_valid(raise_exception=True)
            application = Application.objects.filter(id=self.data.get('id'),creator=self.data.get('user_id')).first()
            return ApplicationSerializerModel(application).data

    class ApplicationChat(serializers.Serializer):
        application_id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        user_demand = serializers.CharField(required=True,error_messages=ErrMessage.char("用户需求"))
        user_select_tables = serializers.ListField(required=False,error_messages=ErrMessage.char("用户选择表"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            
            # 检查user_select_tables是否存在
            if self.data.get("user_select_tables"):
                table_ids = self.data.get("user_select_tables")
                existing_table_count = TableInfo.objects.filter(
                    id__in=table_ids,
                    datasource_id=self.data.get("datasource_id")
                ).count()
                
                if existing_table_count != len(table_ids):
                    raise ExceptionCodeConstants.TABLE_NOT_EXIST.value.to_app_api_exception()

        def chat(self):
            self.is_valid(raise_exception=True)
            # 根据 application_id 获取 application
            application = Application.objects.filter(id=self.data.get("application_id")).first()
            if not application:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()
            # 新增一条聊天信息(初始化所属应用，此次对话的id，用户需求)
            # todo 考虑事务
            chat_id = str(uuid.uuid1())
            ApplicationChatInfo.objects.create(application=application, id=chat_id, user_demand=self.data.get("user_demand"))
            
            # 开启工作流进行聊天
            model = self.get_model(application)
            if model is None:
                raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()
            manager = PipelineManager.PipelineBuilder().set_agent(model).add_step(TableSelectStep()).add_step(GenerateSqlStep()).add_step(ExecuteSqlStep()).add_step(DataToChartStep()).build()
            print(manager)
            context = {
                'datasource_id': application.datasource.id,
                'user_id': application.creator.id,
                'chat_id': chat_id,
                'user_demand': self.data.get("user_demand"),
                'user_select_tables': [int(id) for id in self.data.get("user_select_tables")] if self.data.get("user_select_tables") else []
            }
            generator = manager.run(context)
            return StreamingHttpResponse(streaming_content=generator, content_type='text/event-stream')
        
        def get_model(self, application) -> BaseChatModel:
            model_config = Model.objects.get(id = application.model_id, created_by=application.creator_id)
            model_provider = ModelProviderConstants[model_config.provider].value
            model = model_provider.get_model(model_config.model_name, rsa_util.decrypt(model_config.api_key), model_config.base_url)
            return model

    class Authentication(serializers.Serializer):
        access_token = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        application_id = serializers.CharField(required=True,error_messages=ErrMessage.char("应用 id"))
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application_access_token = ApplicationAccessToken.objects.filter(access_token=self.data.get('access_token'),application=self.data.get('application_id')).first()
            if not application_access_token:
                raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()

        def authentication(self,request:HttpRequest):
            self.is_valid(raise_exception=True)
            
            application_access_token = ApplicationAccessToken.objects.filter(access_token=self.data.get('access_token'),application=self.data.get('application_id')).first()
            # 网站是否在白名单中
            if application_access_token.white_active:
                if request.META.get('HTTP_X_FORWARDED_FOR') in application_access_token.white_list:
                    pass
                else:
                    raise ExceptionCodeConstants.APPLICATION_NOT_EXIST.value.to_app_api_exception()

            # 创建 jwt token
            return generate_jwt_token(application_access_token.access_token,{"type":"application"})
                
class ApplicationSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
