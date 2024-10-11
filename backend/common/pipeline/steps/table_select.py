from common.pipeline.base_step import BaseStep
from common.pipeline.pipeline_manager import PipelineManager
from common.pipeline.response_util import to_stream_chunk_response, Status
import uuid
from setting.models.table_info import TableInfo
from setting.models.datasource import Datasource
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from rest_framework import serializers
from common.exceptions.exception import ExceptionCodeConstants
from common.response.field_response import ErrMessage
import json


class TableSelectStep(BaseStep):

    class ResponseSchema(BaseModel):
        table_ids: List[int] = Field(description="表的id")
        reason: str = Field(description="选择这些表的理由")
        error: bool = Field(description="是否为数据分析意图")

    class TableSelectStepSerializer(serializers.Serializer):
        user_demand: str = serializers.CharField(required=True, max_length=1000,error_messages=ErrMessage.char("用户需求"))
        user_id: int = serializers.IntegerField(required=True,error_messages=ErrMessage.char("用户 id"))
        datasource_id: int = serializers.IntegerField(required=True,error_messages=ErrMessage.char("数据源 id"))
        user_select_tables: List[int] = serializers.ListField(required=False,error_messages=ErrMessage.char("用户选择表"))
        
        def is_valid(self, *, raise_exception=False):
            # 先进行校验基础字段是否存在
            super().is_valid(raise_exception=True)
            datasource_id = self.data['datasource_id']
            user_id = self.data['user_id']

            # 再进行数据源是否存在校验
            datasource = Datasource.objects.filter(id=datasource_id, created_by=user_id).first()
            if not datasource:
                raise ExceptionCodeConstants.DATASOURCE_NOT_EXIST.value.to_app_api_exception()

    def get_step_serializer(self, manager) -> serializers.Serializer:
        return self.TableSelectStepSerializer(data = manager.context)

    def run_before(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, '开始选择表', Status.START)
        

    def run_after(self, manager:PipelineManager):
        reason = self.context["reason"]
        table_ids = self.context["table_ids"]
        json_data = json.dumps({
            "table_ids": table_ids,
            "reason": reason
        })
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, json_data, Status.COMPLETED)
        
    
    def if_not_continue(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, '我目前只支持数据分析。', Status.ERROR)

    def _run(self, manager:PipelineManager) -> bool:
        user_demand = self.context['user_demand']
        datasource_id = self.context['datasource_id']
        user_select_tables = self.context['user_select_tables'] if self.context['user_select_tables'] else []
        table_info = TableInfo.objects.filter(datasource_id=datasource_id).all()
        manager.context['table_infos'] = table_info
        can_select_tables = ""
        for table in table_info:
            can_select_tables += f"{table.name} (id = {table.id}): {table.summary}\n"
        prompt = ChatPromptTemplate.from_template(self.get_prompt())
        prompt = prompt.invoke({"user_demand":user_demand, "can_select_table":can_select_tables, "user_select_tables":user_select_tables})
        agent = manager.agent
        
        answer = agent.with_structured_output(self.ResponseSchema).invoke(prompt)
        if answer.error:
            return False
        # 存入局部上下文
        self.context["reason"] = answer.reason
        # 求user_select_tables和answer.table_ids两个集合的并集
        user_select_tables = set(self.context['user_select_tables'])
        answer_table_ids = set(answer.table_ids)
        combined_table_ids = list(user_select_tables.union(answer_table_ids))
        self.context["table_ids"] = combined_table_ids

        # 将输出存入全局上下文
        manager.context.update(self.step_output_data())

        return True

    def get_prompt(self):
        return """
    ## 角色

    你是一个 MySQL 专家，你精通各种 sql 查询从不犯错。

    ## 任务

    首先，你需要判断用户的意图是否为数据分析，若意图不是数据分析，则 error 字段为 true。若意图是数据分析，则 error 字段为 false，执行下一步。
    
    然后，你需要根据用户的需求和目前系统中已有的数据库表信息，综合分析要满足用户的需求需要使用哪些表，给出表的 id。并给出选择的理由。

    ## 用户的需求

    {user_demand}

    ## 数据库表

    {can_select_table}

    ## 用户要求你必须使用以下表（若用户没有选择表，则不使用该条件）

    {user_select_tables}
    """

    def step_output_data(self) -> dict:
        return {
            "reason":self.context.get("reason"),
            "table_ids":self.context.get("table_ids")
        }
    
