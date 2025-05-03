#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
明日方舟自动化系统GUI界面
提供图形用户界面，便于操作和监控
"""

import os
import sys
import time
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
from datetime import datetime

# 导入功能模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 由于 EmulatorController 未使用，移除该导入项
# 原导入行已删除，此处无新代码插入
from modules.image_recognition import ImageRecognizer
from modules.game_controller import GameController
from modules.arknights_login import ArknightsLogin
from modules.arknights_recruitment import ArknightsRecruitment
from modules.arknights_base import ArknightsBase
from modules.arknights_combat import ArknightsCombat
from modules.arknights_reward import ArknightsReward
from main import ArknightsAuto

# 配置日志
class TextHandler(logging.Handler):
    """将日志输出到Tkinter文本控件"""
    
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)
        # 在主线程中更新UI
        self.text_widget.after(0, append)

class ArknightsAutoGUI:
    """明日方舟自动化系统GUI类"""
    
    def __init__(self, root):
        """
        初始化GUI界面
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("明日方舟自动化系统")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # 设置白色主题
        self.root.configure(bg='white')
        style = ttk.Style()
        style.configure('TFrame', background='white')
        style.configure('TLabelframe', background='white')
        style.configure('TLabelframe.Label', background='white')
        style.configure('TLabel', background='white')
        style.configure('TButton', background='white')
        style.configure('TCheckbutton', background='white')
        style.configure('TNotebook', background='white')
        style.configure('TNotebook.Tab', background='white')
        
        # 创建自动化实例
        self.auto = None
        self.config_file = "config.json"
        self.config = self._load_default_config()
        
        # 创建任务线程
        self.task_thread = None
        self.is_running = False
        
        # 创建界面
        self._create_ui()
        
        # 加载配置
        self._load_config()
        
        # 设置日志
        self._setup_logging()
        
        # 更新状态
        self._update_status("就绪")
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _load_default_config(self):
        """
        加载默认配置
        
        Returns:
            dict: 默认配置字典
        """
        return {
            "emulator": {
                "host": "127.0.0.1",
                "port": 5037,
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
    
    def _create_ui(self):
        """创建GUI界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame, style='TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建各个标签页
        self.main_tab = ttk.Frame(notebook)
        self.config_tab = ttk.Frame(notebook)
        self.log_tab = ttk.Frame(notebook)
        self.about_tab = ttk.Frame(notebook)
        
        notebook.add(self.main_tab, text="主界面")
        notebook.add(self.config_tab, text="配置")
        notebook.add(self.log_tab, text="日志")
        notebook.add(self.about_tab, text="关于")
        
        # 创建主界面
        self._create_main_tab()
        
        # 创建配置界面
        self._create_config_tab()
        
        # 创建日志界面
        self._create_log_tab()
        
        # 创建关于界面
        self._create_about_tab()
        
        # 创建状态栏
        self.status_bar = ttk.Label(self.root, text="状态: 初始化中...", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_main_tab(self):
        """创建主界面标签页"""
        # 创建左侧任务选择区域
        left_frame = ttk.LabelFrame(self.main_tab, text="任务选择", padding="10", style='TLabelframe')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # 创建任务复选框
        self.task_vars = {}
        tasks = [
            ("login", "游戏登录"),
            ("recruitment", "公开招募"),
            ("base", "基建收菜"),
            ("combat", "上一次作战"),
            ("reward", "领取奖励")
        ]
        
        for key, text in tasks:
            var = tk.BooleanVar(value=True)
            self.task_vars[key] = var
            ttk.Checkbutton(left_frame, text=text, variable=var).pack(anchor=tk.W, pady=2)
        
        # 创建作战设置区域
        combat_frame = ttk.LabelFrame(left_frame, text="作战设置", padding="10", style='TLabelframe')
        combat_frame.pack(fill=tk.X, pady=10)
        
        # 使用理智药剂
        self.use_sanity_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(combat_frame, text="使用理智药剂", variable=self.use_sanity_var).pack(anchor=tk.W)
        
        # 最大作战次数
        ttk.Label(combat_frame, text="最大作战次数:").pack(anchor=tk.W, pady=(5, 0))
        self.max_times_var = tk.StringVar(value="5")
        ttk.Spinbox(combat_frame, from_=1, to=100, textvariable=self.max_times_var, width=5).pack(anchor=tk.W)
        
        # 创建公开招募设置区域
        recruit_frame = ttk.LabelFrame(left_frame, text="公开招募设置", padding="10", style='TLabelframe')
        recruit_frame.pack(fill=tk.X, pady=10)
        
        # 使用加急许可
        self.use_expedited_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(recruit_frame, text="使用加急许可", variable=self.use_expedited_var).pack(anchor=tk.W)
        
        # 创建右侧控制区域
        right_frame = ttk.Frame(self.main_tab, padding="10", style='TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建状态显示区域
        status_frame = ttk.LabelFrame(right_frame, text="状态", padding="10", style='TLabelframe')
        status_frame.pack(fill=tk.X, pady=5)
        
        # 连接状态
        self.connection_status = ttk.Label(status_frame, text="未连接")
        self.connection_status.pack(anchor=tk.W)
        
        # 当前任务
        self.current_task = ttk.Label(status_frame, text="当前任务: 无")
        self.current_task.pack(anchor=tk.W)
        
        # 创建截图显示区域
        screenshot_frame = ttk.LabelFrame(right_frame, text="当前截图", padding="10", style='TLabelframe')
        screenshot_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 截图标签
        self.screenshot_label = ttk.Label(screenshot_frame, text="无截图")
        self.screenshot_label.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮区域
        button_frame = ttk.Frame(right_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=10)
        
        # 连接按钮
        self.connect_button = ttk.Button(button_frame, text="连接模拟器", command=self._connect_emulator)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        # 开始按钮
        self.start_button = ttk.Button(button_frame, text="开始任务", command=self._start_tasks, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_button = ttk.Button(button_frame, text="停止任务", command=self._stop_tasks, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def _create_config_tab(self):
        """创建配置界面标签页"""
        # 创建配置框架
        config_frame = ttk.Frame(self.config_tab, padding="10", style='TFrame')
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建模拟器设置区域
        emulator_frame = ttk.LabelFrame(config_frame, text="模拟器设置", padding="10", style='TLabelframe')
        emulator_frame.pack(fill=tk.X, pady=5)
        
        # 主机地址
        ttk.Label(emulator_frame, text="主机地址:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.host_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(emulator_frame, textvariable=self.host_var).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 端口
        ttk.Label(emulator_frame, text="端口:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.port_var = tk.StringVar(value="5037")
        ttk.Entry(emulator_frame, textvariable=self.port_var).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # 设备序列号
        ttk.Label(emulator_frame, text="设备序列号:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.serial_var = tk.StringVar(value="")
        ttk.Entry(emulator_frame, textvariable=self.serial_var).grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(emulator_frame, text="(留空则连接第一个可用设备)").grid(row=2, column=2, sticky=tk.W)
        
        # 创建目录设置区域
        dir_frame = ttk.LabelFrame(config_frame, text="目录设置", padding="10", style='TLabelframe')
        dir_frame.pack(fill=tk.X, pady=5)
        
        # 模板目录
        ttk.Label(dir_frame, text="模板目录:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.template_dir_var = tk.StringVar(value="assets/templates")
        ttk.Entry(dir_frame, textvariable=self.template_dir_var).grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Button(dir_frame, text="浏览...", command=lambda: self._browse_directory(self.template_dir_var)).grid(row=0, column=2)
        
        # 截图目录
        ttk.Label(dir_frame, text="截图目录:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.screenshot_dir_var = tk.StringVar(value="screenshots")
        ttk.Entry(dir_frame, textvariable=self.screenshot_dir_var).grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Button(dir_frame, text="浏览...", command=lambda: self._browse_directory(self.screenshot_dir_var)).grid(row=1, column=2)
        
        # 设置列权重
        dir_frame.columnconfigure(1, weight=1)
        
        # 创建按钮区域
        button_frame = ttk.Frame(config_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=10)
        
        # 加载配置按钮
        ttk.Button(button_frame, text="加载配置", command=self._load_config_dialog).pack(side=tk.LEFT, padx=5)
        
        # 保存配置按钮
        ttk.Button(button_frame, text="保存配置", command=self._save_config_dialog).pack(side=tk.LEFT, padx=5)
        
        # 恢复默认配置按钮
        ttk.Button(button_frame, text="恢复默认", command=self._reset_config).pack(side=tk.LEFT, padx=5)
    
    def _create_log_tab(self):
        """创建日志界面标签页"""
        # 创建日志框架
        log_frame = ttk.Frame(self.log_tab, padding="10", style='TFrame')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建日志文本框并设置白色背景
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=20)
        self.log_text.configure(bg='white', fg='black')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮区域
        button_frame = ttk.Frame(log_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=5)
        
        # 清空日志按钮
        ttk.Button(button_frame, text="清空日志", command=self._clear_log).pack(side=tk.LEFT, padx=5)
        
        # 保存日志按钮
        ttk.Button(button_frame, text="保存日志", command=self._save_log).pack(side=tk.LEFT, padx=5)
    
    def _create_about_tab(self):
        """创建关于界面标签页"""
        # 创建关于框架
        about_frame = ttk.Frame(self.about_tab, padding="20", style='TFrame')
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(about_frame, text="明日方舟自动化系统", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # 版本
        ttk.Label(about_frame, text="版本: 1.0.0").pack()
        
        # 描述
        description = """
        明日方舟自动化系统是一个基于Python的自动化工具，
        用于辅助玩家完成《明日方舟》游戏中的日常任务。
        
        系统通过图像识别和模拟器控制技术，实现了游戏登录、
        公开招募、基建收菜、作战重放和奖励领取等功能的自动化。
        """
        ttk.Label(about_frame, text=description, justify=tk.CENTER).pack(pady=10)
        
        # 功能列表
        features = """
        主要功能:
        - 游戏登录
        - 公开招募
        - 基建收菜
        - 上一次作战
        - 领取奖励
        """
        ttk.Label(about_frame, text=features, justify=tk.LEFT).pack(pady=10)
        
        # 版权信息
        ttk.Label(about_frame, text="© 2025 明日方舟自动化系统团队").pack(pady=10)
    
    def _setup_logging(self):
        """设置日志"""
        # 创建日志处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setLevel(logging.INFO)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.addHandler(text_handler)
        
        # 记录初始日志
        logging.info("明日方舟自动化系统GUI已启动")
    
    def _update_status(self, status):
        """
        更新状态栏
        
        Args:
            status: 状态文本
        """
        self.status_bar.config(text=f"状态: {status}")
    
    def _update_connection_status(self, connected):
        """
        更新连接状态
        
        Args:
            connected: 是否已连接
        """
        if connected:
            self.connection_status.config(text="已连接")
            self.start_button.config(state=tk.NORMAL)
            self.connect_button.config(state=tk.DISABLED)
        else:
            self.connection_status.config(text="未连接")
            self.start_button.config(state=tk.DISABLED)
            self.connect_button.config(state=tk.NORMAL)
    
    def _update_current_task(self, task):
        """
        更新当前任务
        
        Args:
            task: 任务名称
        """
        self.current_task.config(text=f"当前任务: {task}")
    
    def _update_screenshot(self, image_path):

    def _start_tasks(self):
        """开始任务"""
        if self.is_running:
            messagebox.showwarning("警告", "任务已在运行中")
            return
        
        # 更新配置
        self._update_config_from_ui()
        
        # 检查是否已连接
        if not self.auto or not self.auto.emulator.is_connected():
            messagebox.showerror("错误", "未连接到模拟器，请先连接模拟器")
            return
        
        # 检查是否选择了任务
        if not any(var.get() for var in self.task_vars.values()):
            messagebox.showerror("错误", "请至少选择一个任务")
            return
        
        # 更新自动化实例配置
        self.auto.config["tasks"] = {key: var.get() for key, var in self.task_vars.items()}
        self.auto.config["combat"]["use_sanity_item"] = self.use_sanity_var.get()
        self.auto.config["combat"]["max_times"] = int(self.max_times_var.get())
        self.auto.config["recruitment"]["use_expedited"] = self.use_expedited_var.get()
        
        # 创建并启动任务线程
        self.is_running = True
        self.task_thread = threading.Thread(target=self._run_tasks)
        self.task_thread.daemon = True
        self.task_thread.start()
        
        # 更新界面
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self._update_status("任务运行中...")
        """
        更新截图显示
        
        Args:
            image_path: 截图路径
        """
        try:
            from PIL import Image, ImageTk
            
            # 加载图像
            image = Image.open(image_path)
            
            # 调整图像大小以适应显示区域
            width = self.screenshot_label.winfo_width()
            height = self.screenshot_label.winfo_height()
            
            if width > 1 and height > 1:
                # 计算缩放比例
                image_width, image_height = image.size
                ratio = min(width / image_width, height / image_height)
                new_width = int(image_width * ratio)
                new_height = int(image_height * ratio)
                
                # 缩放图像
                image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # 转换为Tkinter图像
            tk_image = ImageTk.PhotoImage(image)
            
            # 更新标签
            self.screenshot_label.config(image=tk_image)
            self.screenshot_label.image = tk_image  # 保持引用
        except Exception as e:
            logging.error(f"更新截图显示时出错: {str(e)}")
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.isfile(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logging.info(f"已加载配置文件: {self.config_file}")
                
                # 更新界面
                self._update_ui_from_config()
            else:
                logging.warning(f"配置文件不存在: {self.config_file}")
        except Exception as e:
            logging.error(f"加载配置文件时出错: {str(e)}")
    
    def _update_ui_from_config(self):
        """根据配置更新界面"""
        try:
            # 更新模拟器设置
            emulator_config = self.config.get("emulator", {})
            self.host_var.set(emulator_config.get("host", "127.0.0.1"))
            self.port_var.set(str(emulator_config.get("port", 5037)))
            self.serial_var.set(emulator_config.get("device_serial", "") or "")
            
            # 更新目录设置
            self.template_dir_var.set(self.config.get("template_dir", "assets/templates"))
            self.screenshot_dir_var.set(self.config.get("screenshot_dir", "screenshots"))
            
            # 更新任务设置
            tasks = self.config.get("tasks", {})
            for key, var in self.task_vars.items():
                var.set(tasks.get(key, True))
            
            # 更新作战设置
            combat_config = self.config.get("combat", {})
            self.use_sanity_var.set(combat_config.get("use_sanity_item", False))
            self.max_times_var.set(str(combat_config.get("max_times", 5)))
            
            # 更新公开招募设置
            recruitment_config = self.config.get("recruitment", {})
            self.use_expedited_var.set(recruitment_config.get("use_expedited", False))
        except Exception as e:
            logging.error(f"更新界面时出错: {str(e)}")
    
    def _update_config_from_ui(self):
        """根据界面更新配置"""
        try:
            # 更新模拟器设置
            self.config["emulator"] = {
                "host": self.host_var.get(),
                "port": int(self.port_var.get()),
                "device_serial": self.serial_var.get() or None
            }
            
            # 更新目录设置
            self.config["template_dir"] = self.template_dir_var.get()
            self.config["screenshot_dir"] = self.screenshot_dir_var.get()
            
            # 更新任务设置
            self.config["tasks"] = {key: var.get() for key, var in self.task_vars.items()}
            
            # 更新作战设置
            self.config["combat"] = {
                "use_sanity_item": self.use_sanity_var.get(),
                "max_times": int(self.max_times_var.get())
            }
            
            # 更新公开招募设置
            self.config["recruitment"] = {
                "use_expedited": self.use_expedited_var.get()
            }
        except Exception as e:
            logging.error(f"更新配置时出错: {str(e)}")
    
    def _save_config(self, filename=None):
        """
        保存配置到文件
        
        Args:
            filename: 配置文件路径，默认为None（使用当前配置文件）
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 更新配置
            self._update_config_from_ui()
            
            # 保存配置
            save_path = filename or self.config_file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            logging.info(f"配置已保存到: {save_path}")
            return True
        except Exception as e:
            logging.error(f"保存配置时出错: {str(e)}")
            messagebox.showerror("错误", f"保存配置时出错: {str(e)}")
            return False
    
    def _load_config_dialog(self):
        """打开加载配置对话框"""
        filename = filedialog.askopenfilename(
            title="加载配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                
                self.config_file = filename
                logging.info(f"已加载配置文件: {filename}")
                
                # 更新界面
                self._update_ui_from_config()
                
                messagebox.showinfo("成功", f"已加载配置文件: {filename}")
            except Exception as e:
                logging.error(f"加载配置文件时出错: {str(e)}")
                messagebox.showerror("错误", f"加载配置文件时出错: {str(e)}")
    
    def _save_config_dialog(self):
        """打开保存配置对话框"""
        filename = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            if self._save_config(filename):
                self.config_file = filename
                messagebox.showinfo("成功", f"配置已保存到: {filename}")
    
    def _reset_config(self):
        """恢复默认配置"""
        if messagebox.askyesno("确认", "确定要恢复默认配置吗？"):
            self.config = self._load_default_config()
            self._update_ui_from_config()
            logging.info("已恢复默认配置")
    
    def _browse_directory(self, var):
        """
        浏览目录对话框
        
        Args:
            var: 存储目录路径的变量
        """
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            var.set(directory)
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        logging.info("日志已清空")
    
    def _save_log(self):
        """保存日志"""
        filename = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                logging.info(f"日志已保存到: {filename}")
                messagebox.showinfo("成功", f"日志已保存到: {filename}")
            except Exception as e:
                logging.error(f"保存日志时出错: {str(e)}")
                messagebox.showerror("错误", f"保存日志时出错: {str(e)}")
    
    def _connect_emulator(self):
        """连接模拟器"""
        def connect_thread():
            try:
                # 创建游戏控制器
                self.auto = ArknightsAuto({
                    "emulator_path": "",
                    "adb_path": "",
                    "host": self.host_var.get(),
                    "port": int(self.port_var.get())
                })
                
                # 在后台线程执行连接
                connected = self.auto.login_module.connect(self.auto.config["emulator"]["device_serial"])
                
                # 在主线程更新UI
                self.root.after(0, lambda: self._handle_connection_result(connected))
            except Exception as e:
                self.root.after(0, lambda e=e: self._handle_connection_error(e))
def __init__(self, config):
    if not isinstance(config.get('emulator_path'), str) or not os.path.exists(config['emulator_path']):
        raise FileNotFoundError(f"模拟器路径不存在: {config['emulator_path']}")
    if not isinstance(config.get('adb_path'), str) or not os.path.exists(config['adb_path']):
        raise FileNotFoundError(f"ADB路径不存在: {config['adb_path']}")
        # 禁用连接按钮并显示状态
        self.connect_button.config(state=tk.DISABLED)
        self._update_status("正在连接模拟器...")
        
        # 启动后台线程
        threading.Thread(target=connect_thread, daemon=True).start()

    def _handle_connection_result(self, connected):
        """处理连接结果"""
        if connected:
            self._update_status("连接成功")
            self._update_connection_status(True)
            messagebox.showinfo("成功", "模拟器连接成功")
        else:
            self._update_status("连接失败")
            self._update_connection_status(False)
            messagebox.showerror("错误", "无法连接到模拟器")

    def _handle_connection_error(self, error):
        """处理连接异常"""
        self._update_status(f"连接错误: {str(error)}")
        self._update_connection_status(False)
        messagebox.showerror("严重错误", f"连接过程中发生异常:\n{str(error)}")
    
    def _start_tasks(self):
        """开始任务"""
        if self.is_running:
            messagebox.showwarning("警告", "任务已在运行中")
            return
        
        # 更新配置
        self._update_config_from_ui()
        
        # 检查是否已连接
        if not self.auto or not self.auto.emulator.is_connected():
            messagebox.showerror("错误", "未连接到模拟器，请先连接模拟器")
            return
        
        # 检查是否选择了任务
        if not any(var.get() for var in self.task_vars.values()):
            messagebox.showerror("错误", "请至少选择一个任务")
            return
        
        # 更新自动化实例配置
        self.auto.config["tasks"] = {key: var.get() for key, var in self.task_vars.items()}
        self.auto.config["combat"]["use_sanity_item"] = self.use_sanity_var.get()
        self.auto.config["combat"]["max_times"] = int(self.max_times_var.get())
        self.auto.config["recruitment"]["use_expedited"] = self.use_expedited_var.get()
        
        # 创建并启动任务线程
        self.is_running = True
        self.task_thread = threading.Thread(target=self._run_tasks)
        self.task_thread.daemon = True
        self.task_thread.start()
        
        # 更新界面
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self._update_status("任务运行中...")
    
    def _run_tasks(self):
        """运行任务线程"""
        try:
            logging.info("开始运行任务...")
            
            # 运行任务
            self.auto.run_tasks()
            
            # 任务完成
            logging.info("所有任务执行完成")
            self.root.after(0, self._on_tasks_completed)
        except Exception as e:
            logging.error(f"运行任务时出错: {str(e)}")
            self.root.after(0, lambda: self._on_tasks_error(str(e)))
    
    def _stop_tasks(self):
        """停止任务"""
        if not self.is_running:
            return
        
        logging.info("正在停止任务...")
        self._update_status("正在停止任务...")
        
        # 设置停止标志
        self.is_running = False
        
        # 更新界面
        self.stop_button.config(state=tk.DISABLED)
    
    def _on_tasks_completed(self):
        """任务完成回调"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self._update_status("任务已完成")
        self._update_current_task("无")
        messagebox.showinfo("完成", "所有任务已执行完成")
    
    def _on_tasks_error(self, error_msg):
        """任务错误回调"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self._update_status("任务出错")
        self._update_current_task("无")
        messagebox.showerror("错误", f"运行任务时出错: {error_msg}")
    
    def _on_close(self):
        """关闭窗口回调"""
        if self.is_running:
            if not messagebox.askyesno("确认", "任务正在运行中，确定要退出吗？"):
                return
            
            # 停止任务
            self._stop_tasks()
        
        # 保存配置
        if messagebox.askyesno("确认", "是否保存当前配置？"):
            self._save_config()
        
        # 关闭窗口
        self.root.destroy()

        def _start_tasks(self):
            # ...
            self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
            self.progress_bar.pack(pady=10)
            self.progress_bar['value'] = 0
            # ...

        def _update_progress(self, value):
            self.progress_bar['value'] = value
            self.root.update_idletasks()

def main():
    """主函数"""
    # 创建根窗口
    root = tk.Tk()
    
    # 设置白色主题
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置全局样式
    root.configure(bg='white')
    style.configure('TFrame', background='white')
    style.configure('TLabelframe', background='white')
    style.configure('TLabelframe.Label', background='white')
    style.configure('TLabel', background='white')
    style.configure('TButton', background='white')
    style.configure('TCheckbutton', background='white')
    style.configure('TNotebook', background='white')
    style.configure('TNotebook.Tab', background='white')
    
    # 创建GUI实例
    app = ArknightsAutoGUI(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()
