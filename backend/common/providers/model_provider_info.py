
class ModelProviderInfo:
    def __init__(self, provider:str, name:str, icon:str):
        self.provider = provider
        self.name = name
        self.icon = icon

    def to_dict(self):
        """
        1. 获取对象的所有非内部属性
        2. 为每个属性创建一个单键字典
        3. 使用 reduce 和 lambda 函数将所有单键字典合并成一个大字典
        """
        return {attr: getattr(self, attr) for attr in vars(self) if not attr.startswith("__")}
        
