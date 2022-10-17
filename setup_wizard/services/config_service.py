import json


class ConfigService:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = json.load(open(self.config_file_path))
    
    def get(self, key):
        return self.config.get(key)
    
    def get_config(self):
        return self.config
