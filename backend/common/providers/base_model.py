from abc import ABC, abstractmethod

class BaseModel(ABC):
    @staticmethod
    @abstractmethod
    def new_instance(self,model_name:str, api_key:str, base_url:str = None, max_tokens:int = 1024, temperature:float = 0.5):
        pass

    @abstractmethod
    def test_invoke(self) -> bool:
        pass

    
    