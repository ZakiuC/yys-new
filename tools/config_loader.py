import json
from tools.logger import LogManager

class ConfigLoader:
    def __init__(self, config_path):
        self.logger = LogManager(name="config_loader")
        self.config_path = config_path
        self.config = self.load_config()
        
        
    def load_config(self):
        """
        加载配置文件
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
            self.logger.info(f"加载配置文件成功")
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败：{e}")
            raise Exception(f"加载配置文件失败：{e}")

    def get(self, key, default=None):
        """
        获取配置值，如果不存在则返回默认值
        """
        return self.config.get(key, default)
