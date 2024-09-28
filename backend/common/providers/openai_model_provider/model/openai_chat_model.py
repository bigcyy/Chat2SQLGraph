from common.providers.base_model import BaseModel
from common.providers.model_info import ModelInfo
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class OpenAIChatModel(BaseModel, ChatOpenAI):
    
    @staticmethod
    def new_instance(model_name:str, api_key:str,base_url:str = None, max_tokens:int = 1024, temperature:float = 0.5) -> BaseModel:
        
        return OpenAIChatModel(
            model=model_name,
            base_url=base_url, 
            api_key=api_key, 
            max_tokens=max_tokens, 
            temperature=temperature
        )
    
    def test_invoke(self) -> bool:
        try:
            self.invoke([HumanMessage("Hello, world!")])
            return True
        except Exception as e:
            return False