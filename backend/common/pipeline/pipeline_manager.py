from typing import Type
from .base_step import BaseStep
from .response_util import format_stream_chunk
import uuid
import json
from chat.models import ChatInfo

class PipelineManager:
    def __init__(self, step_chain_head:Type[BaseStep], agent):
        self.step_chain_head = step_chain_head
        self.context = {'all_tokens': 0, 'pipeline_run_time': 0,'sse_message_list': []}
        self.agent = agent

    def run(self, context:dict = None):
        # 初始化上下文
        if context is not None:
            self.context.update(context)
        # 运行工作流
        response_generator = self.step_chain_head.run(self)
        # 发送工作流产生的消息
        for response in response_generator:
            self.context['sse_message_list'].append(response)
            yield format_stream_chunk(response)
        
        # todo 事务
        # 保存整个流程的执行结果
        self.save_context()
        # 保存 sse 消息列表
        self.save_sse_message_list()
    
    def re_run(self, begin_step_key:str, steps_content:dict ,context:dict = None):

        if context is not None:
            self.context.upate(context)

        step = self.step_chain_head
        while step is not None:
            if step.__class__.__name__ == begin_step_key:
                break
            # 复原上下文
            step_content = steps_content[step.__class__.__name__]
            step.context.update(step_content)
            self.context.update(step_content)
            step = step.next_step
        if step is None:
            return
        
        for response in step.run(self):
            yield response

        self.save_context()
        self.save_sse_message_list()
        
    def get_save_context(self) -> str:
        # 保存整个流程的执行结果
        save_dict = {}
        step = self.step_chain_head
        while step is not None:
            save_dict[step.__class__.__name__] = step.get_step_output_data_for_save()
            step = step.next_step
        return json.dumps(save_dict)
    
    def save_context(self):
        chat_id = self.context['chat_id']
        json_str = self.get_save_context()
        # 更新数据库
        ChatInfo.objects.filter(id=chat_id).update(chat_content=json_str)

    def save_sse_message_list(self):
        chat_id = self.context['chat_id']
        json_str = json.dumps(self.context['sse_message_list'])
        ChatInfo.objects.filter(id=chat_id).update(sse_message_list=json_str)

    class PipelineBuilder:
        def __init__(self):
            self.step_chain_head = None
            self.end_step = None
            self.agent = None

        def add_step(self, step:Type[BaseStep]):
            if self.step_chain_head is None:
                self.step_chain_head = step
            else:
                self.end_step.set_next_step(step)
            self.end_step = step
            return self
        
        def set_agent(self, agent):
            self.agent = agent
            return self

        def build(self):
            return PipelineManager(self.step_chain_head, self.agent)

