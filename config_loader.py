import json
import os

class ConfigLoader:
    _instance = None

    def __init__(self, config_path='config.json'):
        self.config_path = os.path.abspath(config_path)
        self.config = self._load_config()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f'配置文件加载失败: {str(e)}')
            return self._create_default_config()

    def _create_default_config(self):
        default_config = {
            "emulator_path": "Z:\\leidian\\LDPlayer9\\dnplayer.exe",
            "adb_path": "Z:\\leidian\\LDPlayer9\\adb.exe",
            "package_name": "com.hypergryph.arknights.bilibili",
            "template_dir": "assets/templates"
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config

    def get(self, key, default=None):
        return self.config.get(key, default)

if __name__ == '__main__':
    config = ConfigLoader.get_instance()
    print(config.get('emulator_path'))