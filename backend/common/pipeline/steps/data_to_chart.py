from common.pipeline.base_step import BaseStep
from common.pipeline.pipeline_manager import PipelineManager
from common.pipeline.response_util import to_stream_chunk_response, Status
import uuid
from langchain_core.prompts import ChatPromptTemplate
import json
from rest_framework import serializers
from common.response.field_response import ErrMessage
from common.serializers.custom_serializer import custom_serializer

class DataToChartStep(BaseStep):

    class DataToChartStepSerializer(serializers.Serializer):
        user_demand = serializers.CharField(required=True,error_messages=ErrMessage.char("用户意图"))
        data = serializers.JSONField(required=True,error_messages=ErrMessage.char("数据"))

    def get_step_serializer(self, manager) -> serializers.Serializer:
        return self.DataToChartStepSerializer(data = manager.context)

    def run_before(self, manager:PipelineManager):
        chat_record_id = uuid.uuid1()
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, '开始将数据转换为图表', Status.START)
        

    def run_after(self, manager:PipelineManager):
        chart_option = self.context['chart_option']
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, chart_option, Status.COMPLETED)
        
    
    def if_not_continue(self, manager:PipelineManager):
        yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, "将数据转换为图表失败", Status.ERROR)

    def _run(self, manager:PipelineManager) -> bool:
        # 获取上下文中的数据
        data= self.context['data']
        user_demand = self.context['user_demand']
        # 调用llm将数据转换为 ECharts option 对象的 json 格式
        prompt = ChatPromptTemplate.from_template(self.get_prompt())
        prompt = prompt.invoke({"user_demand":user_demand, "data":data})
        answer = manager.agent.invoke(prompt)
        # 添加重试逻辑，最多重试3次
        max_retries = 3
        for attempt in range(max_retries):
            try:
                json.loads(answer.content)
                break  # 如果成功解析JSON，跳出循环
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:  # 如果不是最后一次尝试
                    # 重新调用LLM生成答案
                    answer = manager.agent.invoke(prompt)
                else:
                    # 所有尝试都失败，返回False
                    return False
        
        # 将输出存入局部上下文
        self.context['chart_option'] = answer.content
        # 将输出存入全局上下文
        manager.context.update(self.step_output_data())
        return True


    def get_prompt(self):
        return """
    ## 角色

    你是一个精通 ECharts 的开发者，你从不会犯错，你需要准确无误的将数据处理成渲染图表所需要的 option 对象的 json 格式。

    ## 任务

    数据解析成 option 对象的 json 格式 ：你需要分析用户的意图，和最终要生成的 ECharts 图表，将数据处理成渲染图表所需要的 option 对象的 json 格式。

    ## 用户意图

    {user_demand}

    ## 数据

    {data}

    ## 响应格式

    解析后的 Echart option 对象的 json 格式 ，保证所有输出能够直接的正确的被 JSON.parse(optionJson) 所解析成 ECharts option 对象，如果出现错误你将会被解雇！只需要输出 option 对象的 json 格式，不要输出任何其他内容（包括markdown格式的代码块）。
    """

    def step_output_data(self) -> dict:
        return {
            "chart_option":self.context.get("chart_option")
        }

