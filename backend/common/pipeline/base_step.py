from abc import ABC, abstractmethod
from rest_framework import serializers
from .response_util import to_stream_chunk_response, Status

class BaseStep(ABC):
    def __init__(self):
        self.context = {}
        self.next_step = None

    @abstractmethod
    def get_step_serializer(self, manager) -> serializers.Serializer:
        pass

    def validate_params(self, manager):
        """
        校验当前步骤的参数是否合法,如果参数不合法则抛出异常，停止当前及其后续步骤的执行
        如果参数合法则将上下文中的与当前步骤相关的参数放入当前步骤的 context 中
        :param manager: 当前 pipeline 的 manager, 包含当前 pipeline 的上下文信息
        """
        # 获取校验器
        serializer = self.get_step_serializer(manager)
        step_params = {}
        if serializer is not None:
            # 若校验器不为空则进行校验
            serializer.is_valid(raise_exception=True)
            step_params = serializer.data

        # 将校验结果放入当前步骤的 context 中
        self.context.update(step_params)

    @abstractmethod
    def run_before(self, manager):
        """
        执行 before 方法，主要用于向前端发送消息, 在当前步骤的逻辑执行之前执行
        :param manager: 当前 pipeline 的 manager, 包含当前 pipeline 的上下文信息
        """
        pass

    @abstractmethod
    def _run(self, manager) -> bool:
        """
        执行当前步骤的逻辑, 返回是否继续执行下一个步骤，如果抛出异常则不会执行下一个步骤
        :param manager: 当前 pipeline 的 manager, 包含当前 pipeline 的上下文信息
        :return: 是否继续执行下一个步骤
        """
        pass

    @abstractmethod
    def run_after(self, manager):
        """
        执行 after 方法，主要用于向前端发送消息, 在当前步骤的逻辑执行完毕后执行
        若当前步骤的逻辑执行失败，则不会执行 after 方法，而是执行 if_not_continue 方法
        :param manager: 当前 pipeline 的 manager, 包含当前 pipeline 的上下文信息
        """
        pass
    
    @abstractmethod
    def if_not_continue(self, manager):
        """
        执行 if_not_continue 方法，当前步骤的逻辑执行失败时，执行该方法，主要用于向前端发送消息
        :param manager: 当前 pipeline 的 manager, 包含当前 pipeline 的上下文信息
        """
        pass

    def run(self, manager):
        
        # 参数校验
        try:
            self.validate_params(manager)
        except Exception as e:
            yield to_stream_chunk_response(manager.context['chat_id'], self.__class__.__name__, e.message, Status.ERROR)
            return
        
        # 执行 before 方法
        for response in self.run_before(manager):
            yield response
        
        # 执行当前步骤的逻辑
        is_continue = True
        try:
            is_continue = self._run(manager)
        except Exception as e:
            is_continue = False
        
        # 如果当前步骤的逻辑执行失败, 则执行 if_not_continue 方法
        if not is_continue:
            for response in self.if_not_continue(manager):
                yield response
            return
        
        # 执行 after 方法
        for response in self.run_after(manager):
            yield response

        # 运行下一个step
        for response in self.run_next(manager):
            yield response
    
    
    def set_next_step(self, next_step):
        self.next_step = next_step

    def run_next(self, manager):
        if self.next_step is not None:
            for response in self.next_step.run(manager):
                yield response

    @abstractmethod
    def get_step_dict_for_saving(self) -> dict:
        """
        返回需要保存的当前步骤状态字典，在整个 pipeline 执行完毕后，会将这些字典保存到数据库中
        """
        pass