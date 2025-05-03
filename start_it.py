import tkinter as tk
from tkinter import filedialog, messagebox, font
import json
import os
import sys
# 默认配置路径
CONFIG_FILE = "config.json"


class ConfigEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("明日方舟自动化配置编辑器")
        self.entries = {}  # 存储输入框/复选框组件
        self.config = {}

        # 设置中文字体
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="微软雅黑", size=10)

        # 加载配置
        self.load_config()

        # 创建界面
        self.create_widgets()

    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(CONFIG_FILE):
            # 如果不存在则创建默认配置
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.default_config(), f, indent=4, ensure_ascii=False)

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"无法加载配置文件: {e}")
            self.config = self.default_config()

    def default_config(self):
        """返回默认配置"""
        return {
            "emulator": {
                "host": "127.0.0.1",
                "port": 5037,
                "device_serial": None,
                "device_port": 5555,
                "emulator_path": "E:/MuMu/MuMu Player 12",
                "adb_path": "E:/develop/platform-tools/adb.exe"
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


    def launch_main(self):
        """点击按钮后运行 main.py"""
        try:
            # 保存当前配置
            self.save_config()

            # 运行 main.py
            import subprocess
            subprocess.Popen([sys.executable, "main.py"], cwd=os.getcwd())

            messagebox.showinfo("成功", "已启动 main.py！")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")
    def create_widgets(self):
        """动态创建 GUI 控件"""

        row = 0
        for section_key, section_value in self.config.items():
            section_label = {
                "emulator": "模拟器设置",
                "template_dir": "模板目录",
                "screenshot_dir": "截图保存目录",
                "tasks": "启用任务",
                "combat": "战斗设置",
                "recruitment": "招募设置"
            }.get(section_key, section_key)

            tk.Label(self.root, text=f"{section_label}:", font=("微软雅黑", 10, "bold")).grid(
                row=row, column=0, sticky="w", padx=10, pady=(10, 0)
            )
            row += 1

            if isinstance(section_value, dict):
                for key, value in section_value.items():
                    zh_key = {
                        "host": "主机地址",
                        "port": "端口",
                        "device_serial": "设备序列号",
                        "device_port": "设备连接端口",
                        "emulator_path": "模拟器路径",
                        "adb_path": "ADB 路径",
                        "template_dir": "模板目录",
                        "screenshot_dir": "截图目录",
                        "login": "登录",
                        "recruitment": "公开招募",
                        "base": "基建",
                        "combat": "作战",
                        "reward": "奖励",
                        "use_sanity_item": "使用理智药",
                        "max_times": "最大次数",
                        "use_expedited": "使用加急许可"
                    }.get(key, key)

                    self.create_input_widget(row, section_key, key, value, zh_key)
                    row += 1
            else:
                zh_section = {
                    "template_dir": "模板目录",
                    "screenshot_dir": "截图目录"
                }.get(section_key, section_key)

                self.create_input_widget(row, None, section_key, section_value, zh_section)
                row += 1

        # 创建按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        # 保存配置按钮
        save_button = tk.Button(button_frame, text="保存配置", command=self.save_config, width=10)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # 启动程序按钮
        launch_button = tk.Button(button_frame, text="启动程序", command=self.launch_main, width=10)
        launch_button.pack(side=tk.LEFT, padx=5)

    def create_input_widget(self, row, parent_key, key, value, display_name=None):
        """根据值类型创建对应的输入控件"""
        display_name = display_name or key
        label = tk.Label(self.root, text=f"  {display_name}:")
        label.grid(row=row, column=0, sticky="w", padx=10)

        if isinstance(value, bool):
            var = tk.BooleanVar(value=value)
            checkbox = tk.Checkbutton(self.root, variable=var)
            checkbox.grid(row=row, column=1, sticky="w")
            self.entries[(parent_key, key)] = var
        elif isinstance(value, (int, float)):
            entry = tk.Entry(self.root)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, sticky="ew")
            self.entries[(parent_key, key)] = entry
        else:
            entry = tk.Entry(self.root)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, sticky="ew")
            self.entries[(parent_key, key)] = entry

    def save_config(self):
        """保存当前界面的配置到 JSON 文件"""
        try:
            for (parent_key, key), widget in self.entries.items():
                if parent_key is None:
                    # 顶层字段
                    value = self.get_value_from_widget(widget, type(self.config[key]))
                    self.config[key] = value
                else:
                    value = self.get_value_from_widget(widget, type(self.config[parent_key][key]))
                    self.config[parent_key][key] = value

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def get_value_from_widget(self, widget, expected_type):
        """从控件中提取值，并转换为期望的类型"""
        if isinstance(widget, tk.Entry):
            val = widget.get().strip()
            if expected_type == int:
                return int(val)
            elif expected_type == float:
                return float(val)
            elif expected_type == str:
                return val
            elif expected_type == type(None) and val.lower() == "null":
                return None
            return val
        elif isinstance(widget, tk.BooleanVar):
            return widget.get()
        else:
            return widget.get()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditorApp(root)
    root.mainloop()