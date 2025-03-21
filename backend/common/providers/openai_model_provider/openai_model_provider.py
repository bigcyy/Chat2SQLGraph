from common.providers.model_provider_info import ModelProviderInfo
from common.providers.model_info import ModelInfo, ModelInfoManager
from common.providers.base_model_provider import BaseModelProvider
from common.providers.openai_model_provider.model.openai_chat_model import OpenAIChatModel
from common.providers.openai_model_provider.openai_model_info_manager import OpenAIModelInfoManager

class OpenAIModelProvider(BaseModelProvider):
    def __init__(self):
        model_info_manager = ModelInfoManager \
            .Builder(OpenAIModelInfoManager) \
            .add_model(ModelInfo("gpt-4o", "gpt-4o", OpenAIChatModel)) \
            .add_model(ModelInfo("gpt-4o-mini", "gpt-4o-mini", OpenAIChatModel)) \
            .build()
        self.model_info_manager = model_info_manager

    def get_model_info_manager(self) -> ModelInfoManager:
        return self.model_info_manager

    def get_model_provider_info(self):
        return ModelProviderInfo(
            provider="openai_model_provider", 
            name="OpenAI", 
            icon="https://github.com/bigcyy/Chat2SQLGraph/blob/main/backend/common/providers/openai_model_provider/icon/openai_icon_svg"
        )
