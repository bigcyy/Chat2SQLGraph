import os
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

class Config(dict):
    defaults = {
        # 数据库相关配置
        "DB_NAME": "chat2sqlgraph",
        "DB_HOST": "127.0.0.1",
        "DB_PORT": 5432,
        "DB_USER": "postgres",
        "DB_PASSWORD": "postgres",
        "DB_ENGINE": "django.db.backends.postgresql_psycopg2",
    }

    def __init__(self):
        super().__init__(self)
        for key in self.defaults:
            self[key] = self.defaults[key]

    def get_db_settings(self) -> dict:
        return {
            "NAME": self.get('DB_NAME'),
            "HOST": self.get('DB_HOST'),
            "PORT": self.get('DB_PORT'),
            "USER": self.get('DB_USER'),
            "PASSWORD": self.get('DB_PASSWORD'),
            "ENGINE": self.get('DB_ENGINE')
        }


class ConfigManager:
    config_class = Config

    def __init__(self, config_root_path:str):
        self.config_root_path = config_root_path
        self.config = self.config_class()

    def load_config_from_yaml(self) -> None:
        """
        从yaml文件中加载配置
        """
        for file in ['config_example.yml', 'config.yaml', 'config.yml']:
            if not os.path.isfile(os.path.join(self.config_root_path, file)):
                continue
            loaded = self.from_yaml(file)
            if loaded:
                return True
        
        msg = """
                Error: No config file found.
            """
        raise ImportError(msg)

    def from_yaml(self, filename: str) -> bool:
        """
        从yaml文件中加载配置
        """
        file_path = os.path.join(self.config_root_path, filename)
        try:
            with open(file_path, 'rt', encoding='utf8') as f:
                obj = yaml.safe_load(f)
        except IOError as e:
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        if obj:
            # 将yaml文件中的配置映射到config对象中
            return self.from_mapping(obj)
        # 如果yaml文件为空，则直接返回True
        return True

    def from_mapping(self, *mapping, **kwargs):
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got %d' % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                if key.isupper():
                    self.config[key] = value
        return True

    @classmethod
    def load_user_config(cls, config_root_path: str = None):
        """
        加载用户配置，如果config_root_path为空，则使用PROJECT_DIR作为配置根路径
        """
        if config_root_path is None:
            config_root_path = PROJECT_DIR

        manager = cls(config_root_path)
        manager.load_config_from_yaml()
        return manager.config
            
            
