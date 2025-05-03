from modules.emulator import EmulatorController

default_config = {
            "emulator": {
                "host": "127.0.0.1",
                "port": 5037,
                "emulator_path": "E:/MuMu/MuMu Player 12",
                "adb_path": "E:/develop/platform-tools/adb.exe",
                "device_serial": None
            },
            "template_dir": "assets/templates",
            "screenshot_dir": "screenshots",
            "tasks": {
                "login": True,
                "recruitment": True,
                "base": True,
                "combat": True,
                "reward": True
            },
            "combat": {
                "use_sanity_item": False,
                "max_times": 5
            },
            "recruitment": {
                "use_expedited": False
            }
        }

def test_emulator_connection():

        
        try:
            # 创建模拟器连接器
            emulator = EmulatorController(default_config["emulator"])
            
            # 测试连接
            connected = emulator.connect()
            if not connected:
                return False
            
            screenshot_name = input("请输入截图名称：")
            # 测试截图
            screenshot = emulator.take_screenshot("./temp/" + screenshot_name + ".png")
            
            # 断开连接
            emulator.disconnect()
            
            return True
        except Exception as e:
            return False
        
if  __name__ == "__main__":
    test_emulator_connection()