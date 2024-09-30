from common.pipeline.base_step import BaseStep
from common.pipeline.pipeline_manager import PipelineManager
from common.pipeline.response_util import to_stream_chunk_response, Status
import uuid
import pymysql
from common.exceptions.exception import ExceptionCodeConstants
from setting.models import Datasource
from rest_framework import serializers
from common.response.field_response import ErrMessage
import json
from common.utils import rsa_util
class ExecuteSqlStep(BaseStep):

    class ExecuteSqlStepSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        sql = serializers.CharField(required=True,error_messages=ErrMessage.char("sql"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        datasource_id = self.data['datasource_id']
        user_id = self.data['user_id']

        datasource = Datasource.objects.filter(id=datasource_id, created_by=user_id).first()
        if not datasource:
            raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()

    def get_step_serializer(self, manager) -> serializers.Serializer:
        return self.ExecuteSqlStepSerializer(data = manager.context)
    
    def run_before(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, '开始执行sql', Status.START)
        

    def run_after(self, manager:PipelineManager):
        chat_record_id = uuid.uuid1()
        data = manager.context['data']
        json_data = json.dumps({
            "data": data
        })
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, json_data, Status.COMPLETED)
        
    
    def if_not_continue(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, "sql执行失败", Status.ERROR)
        
    def _run(self, manager:PipelineManager) -> bool:

        sql = self.context['sql']
        datasource_id = self.context['datasource_id']
        
        datasource = Datasource.objects.filter(id=datasource_id).first()
        try:
            client = pymysql.connect(host=rsa_util.decrypt(datasource.url),port=datasource.port, user=datasource.username, password=rsa_util.decrypt(datasource.password), database=datasource.database_name)
            cursor = client.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            client.close()
            
        except Exception as e:
            return False
        # 写入局部上下文
        self.context['data'] = data
        # 写入全局上下文
        manager.context.update(self.get_step_dict_for_saving())
        return True

    def get_step_dict_for_saving(self) -> dict:
        return {
            "data": self.context.get("data")
        }
