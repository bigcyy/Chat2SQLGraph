from common.providers.model_info import ModelInfoManager
from common.providers.base_model import BaseModel
from common.providers.openai_model_provider.model.openai_chat_model import OpenAIChatModel
from typing import Type

class OpenAIModelInfoManager(ModelInfoManager):
    def get_private_model_adapter(self) -> Type[BaseModel]:
        return OpenAIChatModel
