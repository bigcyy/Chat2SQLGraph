from enum import Enum
from common.providers.openai_model_provider.openai_model_provider import OpenAIModelProvider
class ModelProviderConstants(Enum):
    openai_model_provider = OpenAIModelProvider()
    # ANTHROPIC = "anthropic"