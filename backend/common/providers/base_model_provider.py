from common.providers.model_info import ModelInfoManager
from abc import ABC,abstractmethod
from common.providers.model_provider_info import ModelProviderInfo
from common.providers.base_model import BaseModel

class BaseModelProvider(ABC):

    @abstractmethod
    def get_model_info_manager(self) -> ModelInfoManager:
        pass

    @abstractmethod
    def get_model_provider_info(self) -> ModelProviderInfo:
        pass

    def model_is_valid(self, model_name:str, api_key:str, base_url:str = None) -> bool:
        # 验证是否传入模型名
        if model_name is None or model_name == "":
            return False
        # 验证是否传入api_key
        if api_key is None or api_key == "":
            return False
        # 是否存在该模型
        model_info_manager = self.get_model_info_manager()
        model_info = model_info_manager.get_model_by_name(model_name)
        if model_info is None:
            return False
        # 获取模型实例
        model = self.get_model(model_name, api_key, base_url)
        # 尝试调用模型
        return model.test_invoke()

    def get_model(self, model_name:str, api_key:str, base_url:str = None) -> BaseModel:
        model_info = self.get_model_info_manager().get_model_by_name(model_name)
        if model_info is None:
            return None
        return model_info.get_class_name().new_instance(model_name=model_name, api_key = api_key, base_url = base_url)


