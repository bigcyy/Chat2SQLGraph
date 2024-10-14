from typing import Type
from abc import ABC, abstractmethod
from common.providers.base_model import BaseModel


class ModelInfo:
    def __init__(self, name:str, desc:str, class_name:Type[BaseModel]) -> None:
        self.name = name
        self.desc = desc
        self.class_name = class_name
    
    def get_name(self) -> str:
        return self.name

    def get_desc(self) -> str:
        return self.desc
    
    def get_class_name(self) -> Type[BaseModel]:
        return self.class_name
    
    def to_dict(self) -> dict:
        return {attr : getattr(self, attr) 
                for attr in vars(self) if not attr.startswith("__") and not attr == 'class_name'}

class ModelInfoManager(ABC):
    def __init__(self) -> None:
        self.model_list = []
    
    def add_model(self, model:ModelInfo):
        self.model_list.append(model)
    
    def get_model_list(self) -> list:
        return self.model_list
    
    def get_model_by_name(self, name:str) -> ModelInfo:
        for model in self.model_list:
            if model.get_name() == name:
                return model
            
        return ModelInfo(name, "私有模型", self.get_private_model_adapter())
    
    @abstractmethod
    def get_private_model_adapter(self) -> Type[BaseModel]:
        pass

    class Builder:
        def __init__(self, model_info_manager_class:Type) -> None:
            self.model_info_manager = model_info_manager_class()
        
        def add_model(self, model:ModelInfo):
            self.model_info_manager.add_model(model)
            return self
        
        def build(self):
            return self.model_info_manager

