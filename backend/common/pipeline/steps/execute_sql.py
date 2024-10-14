from common.pipeline.base_step import BaseStep
from common.pipeline.pipeline_manager import PipelineManager
from common.pipeline.response_util import to_stream_chunk_response, Status
import uuid
import pymysql
from common.exceptions.exception import ExceptionCodeConstants
from setting.models.datasource import Datasource
from rest_framework import serializers
from common.response.field_response import ErrMessage
import json
from common.utils import rsa_util
from common.serializers.custom_serializer import custom_serializer
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
        output_data = self.step_output_data()
        json_data = json.dumps(output_data, default=custom_serializer)
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, json_data, Status.COMPLETED)
        
    
    def if_not_continue(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, "SQL执行失败，请检查数据库是否可以连接。", Status.ERROR)
        
    def _run(self, manager:PipelineManager) -> bool:

        sql = self.context['sql']
        datasource_id = self.context['datasource_id']
        
        datasource = Datasource.objects.filter(id=datasource_id).first()
        try:
            client = pymysql.connect(host=rsa_util.decrypt(datasource.url),port=datasource.port, user=datasource.username, password=rsa_util.decrypt(datasource.password), database=datasource.database_name)
            cursor = client.cursor()
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            client.close()
            
        except Exception as e:
            return False
        # 写入局部上下文
        self.context['data'] = data
        self.context['columns'] = columns
        # 将输出存入全局上下文
        output_data = self.step_output_data()
        json_data = json.dumps(output_data, default=custom_serializer)
        manager.context.update({"data": json_data})
        return True

    def step_output_data(self) -> dict:
        return {
            "columns": self.context.get("columns"),
            "data": self.context.get("data")
        }
        
