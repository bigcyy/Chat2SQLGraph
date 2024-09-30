from rest_framework import serializers
from common.response.field_response import ErrMessage
from common.exceptions.exception import ExceptionCodeConstants
from setting.models.datasource import Datasource
from .models import ChatInfo
from django.http import StreamingHttpResponse
from setting.models.model import Model
from common.providers.model_provider_constants import ModelProviderConstants
from common.pipeline.pipeline_manager import PipelineManager
from common.pipeline.steps.table_select import TableSelectStep
from common.pipeline.steps.generate_sql import GenerateSqlStep
from common.pipeline.steps.execute_sql import ExecuteSqlStep
from common.pipeline.steps.data_to_chart import DataToChartStep
from user.models import User
from common.utils import rsa_util
import json
from langchain_core.language_models import BaseChatModel

class ChatSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            
        def list(self):
            self.is_valid()
            chat_infos = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id")).all()
            return [self.to_dict(chat_info) for chat_info in chat_infos]
        
        def to_dict(self,chat_info):
            return {
                "id":chat_info.id,
                "datasource_id":chat_info.datasource_id.id,
                "user_id":chat_info.user_id.id,
                "user_demand":chat_info.user_demand,
                "created_at":chat_info.created_at,
                "updated_at":chat_info.updated_at,
            }
        
    class Open(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()

        def chat(self):
            self.is_valid(raise_exception=True)
            # 保存到数据库
            # todo 先保存到缓存，当正式使用时，保存到数据库
            datasource = Datasource(id = self.data.get("datasource_id"))
            user = User(id = self.data.get("user_id"))
            chat_info = ChatInfo.objects.create(datasource_id=datasource,user_id=user)
            return chat_info.id

    class Delete(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        chat_id = serializers.CharField(required=True,error_messages=ErrMessage.char("聊天 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            # 检查聊天是否存在
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            if chat_info is None:
                raise ExceptionCodeConstants.CHAT_NOT_EXIST.value.to_app_api_exception()

        def delete(self):
            self.is_valid(raise_exception=True)
            ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).delete()
            

class ChatMessageSerializer(serializers.Serializer):
    class Start(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        chat_id = serializers.CharField(required=True,error_messages=ErrMessage.char("聊天 id"))
        user_demand = serializers.CharField(required=True,error_messages=ErrMessage.char("用户需求"))
        model_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("模型 id"))
    
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            # 模型是否存在
            model = Model.objects.filter(created_by=self.data.get("user_id"),id=self.data.get("model_id")).first()
            if model is None:
                raise ExceptionCodeConstants.MODEL_NOT_EXIST.value.to_app_api_exception()
            # 检查聊天是否存在
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            if chat_info is None:
                raise ExceptionCodeConstants.CHAT_NOT_EXIST.value.to_app_api_exception()
        def chat(self):
            self.is_valid(raise_exception=True)
            
            # 更新聊天信息的user_demand
            ChatInfo.objects.filter(
                datasource_id=self.data.get("datasource_id"),
                user_id=self.data.get("user_id"),
                id=self.data.get("chat_id")
            ).update(user_demand=self.data.get("user_demand"))
            
            model = self.get_model()
            manager = PipelineManager.PipelineBuilder().set_agent(model).add_step(TableSelectStep()).add_step(GenerateSqlStep()).add_step(ExecuteSqlStep()).add_step(DataToChartStep()).build()
            context = {
                'datasource_id': self.data.get("datasource_id"),
                'user_id': self.data.get("user_id"),
                'chat_id': self.data.get("chat_id"),
                'user_demand': self.data.get("user_demand")
            }
            generator = manager.run(context)
            return StreamingHttpResponse(streaming_content=generator, content_type='text/event-stream')
        
        def get_model(self) -> BaseChatModel:
            model_config = Model.objects.get(id = self.data.get("model_id"), created_by=self.data.get("user_id"))
            model_provider = ModelProviderConstants[model_config.provider].value
            model = model_provider.get_model(model_config.model_name, rsa_util.decrypt(model_config.api_key), model_config.base_url)
            return model
        
    class QueryAll(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()

        def list(self):
            self.is_valid(raise_exception=True)
            chat_infos = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id")).all()
            return [self.to_dict(chat_info) for chat_info in chat_infos]
        
        def to_dict(self,chat_info):
            return {
                "id":chat_info.id,
                "datasource_id":chat_info.datasource_id.id,
                "user_id":chat_info.user_id.id,
                "user_demand":chat_info.user_demand,
                "created_at":chat_info.created_at,
                "updated_at":chat_info.updated_at,
            }
    
    class QueryOne(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        chat_id = serializers.CharField(required=True,error_messages=ErrMessage.char("聊天 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            # 检查聊天是否存在
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            if chat_info is None:
                raise ExceptionCodeConstants.CHAT_NOT_EXIST.value.to_app_api_exception()
            
        def one(self):
            self.is_valid(raise_exception=True)
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            return self.to_dict(chat_info)
        
        def to_dict(self,chat_info):
            return {
                "id":chat_info.id,
                "datasource_id":chat_info.datasource_id.id,
                "user_id":chat_info.user_id.id,
                "user_demand":chat_info.user_demand,
                "chat_content":json.loads(chat_info.chat_content),
                "created_at":chat_info.created_at,
                "updated_at":chat_info.updated_at,

            }
    
    class UpdateDemand(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        chat_id = serializers.CharField(required=True,error_messages=ErrMessage.char("聊天 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        user_demand = serializers.CharField(required=True,error_messages=ErrMessage.char("用户需求"))
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            
            # 检查聊天是否存在
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            if chat_info is None:
                raise ExceptionCodeConstants.CHAT_NOT_EXIST.value.to_app_api_exception()
            
        def update(self):
            self.is_valid(raise_exception=True)
            model_config = Model.objects.get(created_by=self.data.get("user_id"),id=self.data.get("model_id"))
            model_provider = ModelProviderConstants.openai_model_provider.value
            model = model_provider.get_model(model_config.model_name, rsa_util.decrypt(model_config.api_key), model_config.base_url)
            manager = PipelineManager.PipelineBuilder().set_agent(model).add_step(TableSelectStep()).add_step(GenerateSqlStep()).add_step(ExecuteSqlStep()).add_step(DataToChartStep()).build()
            context = {
                'datasource_id': self.data.get("datasource_id"),
                'user_id': self.data.get("user_id"),
                'chat_id': self.data.get("chat_id"),
                'user_demand': self.data.get("user_demand")
            }
            generator = manager.run(context)
            return StreamingHttpResponse(streaming_content=generator, content_type='text/event-stream')
    
    class UpdateSql(serializers.Serializer):
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        chat_id = serializers.CharField(required=True,error_messages=ErrMessage.char("聊天 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        sql = serializers.CharField(required=False,error_messages=ErrMessage.char("sql"))
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            
            # 检查聊天是否存在
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            if chat_info is None:
                raise ExceptionCodeConstants.CHAT_NOT_EXIST.value.to_app_api_exception()
            
        def update(self):
            self.is_valid(raise_exception=True)
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            
            steps_content = json.loads(chat_info.chat_content)
            # 根据前端的参数更新步骤上下文
            steps_content['GenerateSqlStep']['sql'] = self.data.get("sql")

            model_config = Model.objects.get(created_by=self.data.get("user_id"),id=self.data.get("model_id"))
            model_provider = ModelProviderConstants.openai_model_provider.value
            model = model_provider.get_model(model_config.model_name, rsa_util.decrypt(model_config.api_key), model_config.base_url)
            manager = PipelineManager.PipelineBuilder().set_agent(model).add_step(TableSelectStep()).add_step(GenerateSqlStep()).add_step(ExecuteSqlStep()).add_step(DataToChartStep()).build()
            
            context = {
                'datasource_id': self.data.get("datasource_id"),
                'user_id': self.data.get("user_id"),
                'chat_id': chat_info.id,
                'user_demand': chat_info.user_demand
            }
            
            responses_generator = manager.re_run(begin_step_key = "ExecuteSqlStep", steps_content=steps_content, context = context)
            return StreamingHttpResponse(streaming_content=responses_generator, content_type='text/event-stream')

    class UpdateTables(serializers.Serializer):
        
        chat_id = serializers.CharField(required=True,error_messages=ErrMessage.char("聊天 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        table_ids = serializers.ListField(required=False,error_messages=ErrMessage.char("表 id 列表"))
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 检查数据源是否存在
            datasource = Datasource.objects.filter(id=self.data.get("datasource_id"),created_by=self.data.get("user_id")).first()
            if datasource is None:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()
            
            # 检查聊天是否存在
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            if chat_info is None:
                raise ExceptionCodeConstants.CHAT_NOT_EXIST.value.to_app_api_exception()
            
        def update(self):
            self.is_valid(raise_exception=True)
            chat_info = ChatInfo.objects.filter(datasource_id=self.data.get("datasource_id"),user_id=self.data.get("user_id"),id=self.data.get("chat_id")).first()
            
            step_content = json.loads(chat_info.chat_content)
            # 根据前端的参数更新步骤上下文
            step_content['TableSelectStep']['table_ids'] = self.data.get("table_ids")

            model_config = Model.objects.get(created_by=self.data.get("user_id"),id=self.data.get("model_id"))
            model_provider = ModelProviderConstants.openai_model_provider.value
            model = model_provider.get_model(model_config.model_name, rsa_util.decrypt(model_config.api_key), model_config.base_url)
            manager = PipelineManager.PipelineBuilder().set_agent(model).add_step(TableSelectStep()).add_step(GenerateSqlStep()).add_step(ExecuteSqlStep()).add_step(DataToChartStep()).build()
        
            context = {
                'datasource_id': self.data.get("datasource_id"),
                'user_id': self.data.get("user_id"),
                'chat_id': chat_info.id,
                'user_demand': chat_info.user_demand
            }
            responses_generator = manager.re_run(begin_step_key = "GenerateSqlStep", step_content=step_content,context = context)
            return StreamingHttpResponse(streaming_content=responses_generator, content_type='text/event-stream')
