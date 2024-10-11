from common.pipeline.base_step import BaseStep
from common.pipeline.pipeline_manager import PipelineManager
from common.pipeline.response_util import to_stream_chunk_response, Status
import uuid
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from common.response.field_response import ErrMessage
from rest_framework import serializers
from common.exceptions.exception import ExceptionCodeConstants
from setting.models.datasource import Datasource
from setting.models.table_info import TableInfo

import json
class GenerateSqlStep(BaseStep):

    class ResponseSchema(BaseModel):
        sql: str = Field(description="sql语句，用于查询能够满足用户数据分析和可视化需求的数据，若可以生成sql则此字段必须输出")
        think: str = Field(description="思考过程")

    class GenerateSqlStepSerializer(serializers.Serializer):
        user_demand = serializers.CharField(required=True,error_messages=ErrMessage.char("用户需求"))
        datasource_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        table_ids = serializers.ListField(required=True,error_messages=ErrMessage.char("表 id"))
        user_id = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            datasource_id = self.data['datasource_id']
            user_id = self.data['user_id']
            table_ids = self.data['table_ids']

            # 再进行数据源是否存在校验
            datasource = Datasource.objects.filter(id=datasource_id, created_by=user_id).first()
            if not datasource:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()

            # 再进行表是否存在校验
            table_infos = TableInfo.objects.filter(id__in=table_ids, datasource_id=datasource_id).all()
            if len(table_infos) != len(table_ids):
                raise ExceptionCodeConstants.TABLE_NOT_EXIST.value.to_app_api_exception()

    def get_step_serializer(self, manager) -> serializers.Serializer:
        return self.GenerateSqlStepSerializer(data=manager.context)

    def run_before(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, '开始生成sql', Status.START)
        

    def run_after(self, manager:PipelineManager):
        # 将sql输出到前端
        chat_record_id = uuid.uuid1()
        sql = self.context["sql"]
        think = self.context["think"]
        json_data = json.dumps({
            "sql": sql,
            "think": think
        })
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, json_data, Status.COMPLETED)
        
    
    def if_not_continue(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, '生成sql失败', Status.ERROR)

    def _run(self, manager:PipelineManager) -> bool:
        # 获取llm选择的表的ddl
        table_ids = self.context['table_ids']
        table_infos = TableInfo.objects.filter(id__in=table_ids).all()
        # 将table_infos转换为ddl_string
        ddl_string = ""
        for table_info in table_infos:
            ddl_string += f"{table_info.ddl}\n"
        # 让llm根据ddl生成sql
        prompt = ChatPromptTemplate.from_template(self.get_prompt())
        prompt = prompt.invoke({"user_demand":self.context['user_demand'], "ddl_string":ddl_string})
        agent = manager.agent
        answer = agent.with_structured_output(self.ResponseSchema).invoke(prompt)
        
        # 存入局部上下文
        self.context["sql"] = answer.sql
        self.context["think"] = answer.think
        # 将输出存入全局上下文
        manager.context.update(self.step_output_data())
        return True

    def get_prompt(self):
        return """
    ## 角色

    你是一个 MySQL 专家，你精通各种 sql 查询。同时你也是一个数据分析和可视化专家。能够根据数据分析和可视化需求编写 sql 获取可视化需要的数据。

    ## 任务

    首先，判断提供的数据库表是否能够满足用户数据分析和可视化需求。
    若能满足，则分析用户的数据分析需求，查看数据可视化过程涉及的数据库表，编写sql语句。
    请逐步进行思考，并将思考过程一起输出。

    ## 用户需求

    用户需求：{user_demand}

    ## 可使用的数据库表

    {ddl_string}
    """

    def step_output_data(self) -> dict:
        return {
            "sql": self.context.get("sql"),
            "think": self.context.get("think")
        }
