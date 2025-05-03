#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
明日方舟游戏登录模块
负责启动游戏并完成登录过程
"""

import os
import time
import logging
from modules.emulator import EmulatorController
from .game_controller import GameController

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ArknightsLogin')

class ArknightsLogin:
    """明日方舟登录类，负责游戏启动和登录流程"""
    
    # 明日方舟游戏包名
    PACKAGE_NAME = "com.hypergryph.arknights"
    
    # 登录相关界面元素模板
    TEMPLATES = {
        "pre_start_button":"pre_start_button,png",
        "start_button": "start_button.png",        # 开始游戏按钮
        "login_button": "login_button.png",        # 登录按钮
        "account_login": "account_login.png",      # 账号登录选项
        "username_field": "username_field.png",    # 用户名输入框
        "password_field": "password_field.png",    # 密码输入框
        "confirm_login": "confirm_login.png",      # 确认登录按钮
        "login_success": "login_success.png",      # 登录成功标志（主界面元素）
        "announcement": "announcement.png",        # 公告弹窗
        "close_announcement": "close_announcement.png", # 关闭公告按钮
        "daily_login": "daily_login.png",          # 每日登录奖励弹窗
        "collect_login_reward": "collect_login_reward.png", # 领取登录奖励按钮
    }
    
    def __init__(self, controller=None, template_dir=None):
        """
        初始化明日方舟登录模块
        
        Args:
            controller: GameController实例，如果为None则创建新实例
            template_dir: 模板图像目录，默认为None
        """
        # 初始化游戏控制器
        self.controller = controller if controller else GameController()
        
        # 设置模板目录
        self.template_dir = template_dir
        if not template_dir:
            # 默认使用assets/templates目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.template_dir = os.path.join(os.path.dirname(current_dir), "assets", "templates")
        
        # 加载模板
        self._load_templates()
        
        logger.info("明日方舟登录模块初始化完成")
    
    def _load_templates(self):
        """加载登录相关的模板图像"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            logger.warning(f"模板目录不存在，已创建: {self.template_dir}")
        
        # 加载模板
        for name, filename in self.TEMPLATES.items():
            template_path = os.path.join(self.template_dir, filename)
            if os.path.isfile(template_path):
                self.controller.recognizer.add_template(name, template_path)
                logger.debug(f"已加载模板: {name}")
            else:
                logger.warning(f"模板文件不存在: {template_path}")
    
    def connect(self, device_serial=None):
        """
        连接到模拟器
        
        Args:
            device_serial: 设备序列号，如果为None则连接到第一个可用设备
            
        Returns:
            bool: 连接是否成功
        """
        return self.controller.connect_emulator(device_serial)
    
    def start_game(self, wait_time=30):
        """
        启动明日方舟游戏
        
        Args:
            wait_time: 启动等待时间，默认为30秒
            
        Returns:
            bool: 启动是否成功
        """
        logger.info("正在启动明日方舟游戏...")
        
        # 启动游戏
        if not self.controller.start_app(self.PACKAGE_NAME, wait_time=5):
            logger.error("启动游戏失败")
            return False
        
        # 等待游戏加载
        logger.info(f"等待游戏加载，最多等待 {wait_time} 秒...")
        
        # 等待开始游戏按钮出现
        found, position, _ = self.controller.wait_for_image(
            template_name="pre_start_button",
            timeout=wait_time,
            interval=2.0
        )
        
        if not found:
            logger.error("等待游戏加载超时，未找到开始游戏按钮")
            return False
        self.controller.tap_image("pre_start_button")
        logger.info("游戏已成功启动")
        time.sleep(8)
        return True
    
    def login(self, username=None, password=None, max_retry=3):
        """
        执行登录流程
        
        Args:
            username: 用户名，如果为None则尝试自动登录
            password: 密码，如果为None则尝试自动登录
            max_retry: 最大重试次数，默认为3
            
        Returns:
            bool: 登录是否成功
        """
        logger.info("开始执行登录流程...")
        
        # 尝试登录，最多重试指定次数
        for attempt in range(max_retry):
            logger.info(f"登录尝试 {attempt + 1}/{max_retry}")
            
            # 检查是否已经在主界面（已登录状态）
            if self._check_already_logged_in():
                logger.info("检测到已经登录")
                # 处理登录后的弹窗
                self._handle_post_login_popups()
                return True
            # 尝试直接点击登录按钮（自动登录）
            if self._auto_login():
                # 等待登录完成
                if self._wait_for_login_complete():
                    # 处理登录后的弹窗
                    self._handle_post_login_popups()
                    return True
            # 点击开始游戏按钮
            if not self._click_start_button():
                logger.warning("未找到开始游戏按钮，尝试继续登录流程")
                continue
            
            # 等待登录界面加载
            time.sleep(3)
            
            # 如果需要账号密码登录
            if username and password:
                if not self._account_login(username, password):
                    logger.error(f"账号登录失败，尝试 {attempt + 1}/{max_retry}")
                    continue
            
            # 等待登录完成
            if self._wait_for_login_complete():
                # 处理登录后的弹窗
                self._handle_post_login_popups()
                return True
            
            logger.warning(f"登录未完成，尝试 {attempt + 1}/{max_retry}")
        
        logger.error(f"在 {max_retry} 次尝试后登录失败")
        return False
    
    def _check_already_logged_in(self):
        """
        检查是否已经登录（在主界面）
        
        Returns:
            bool: 是否已登录
        """
        # 截图检查
        self.controller.take_screenshot()
        
        # 检查是否有主界面元素
        found, _, _ = self.controller.find_image(template_name="login_success")
        if found:
            return  True
        found, _, _ = self.controller.find_image(template_name="announcement")
        if found:
            return  True
        found, _, _ = self.controller.find_image(template_name="daily_login")
        if found:
            return  True
        self.controller.tap_image("confirm_collect")
    
    def _click_start_button(self):
        """
        点击开始游戏按钮
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("尝试点击开始游戏按钮...")
        return self.controller.tap_image(template_name="start_button", max_retries=3)
    
    def _auto_login(self):
        """
        尝试自动登录（点击登录按钮）
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("尝试自动登录...")
        return self.controller.tap_image(template_name="login_button", max_retries=3)
    
    def _account_login(self, username, password):
        """
        使用账号密码登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            bool: 操作是否成功
        """
        logger.info("尝试使用账号密码登录...")
        
        # 点击账号登录选项
        if not self.controller.tap_image(template_name="account_login", max_retries=3):
            logger.error("未找到账号登录选项")
            return False
        
        # 等待账号输入界面加载
        time.sleep(2)
        
        # 点击用户名输入框
        if not self.controller.tap_image(template_name="username_field", max_retries=3):
            logger.error("未找到用户名输入框")
            return False
        
        # 输入用户名
        time.sleep(1)
        self.controller.emulator.input_text(username)
        time.sleep(1)
        
        # 点击密码输入框
        if not self.controller.tap_image(template_name="password_field", max_retries=3):
            logger.error("未找到密码输入框")
            return False
        
        # 输入密码
        time.sleep(1)
        self.controller.emulator.input_text(password)
        time.sleep(1)
        # 点击协议
        self.controller.tap(674.5,631.4)
        # 点击确认登录按钮
        if not self.controller.tap_image(template_name="confirm_login", max_retries=3):
            logger.error("未找到确认登录按钮")
            return False
        
        logger.info("账号密码已输入，等待登录...")
        return True
    
    def _wait_for_login_complete(self, timeout=60):
        """
        等待登录完成（进入主界面）
        
        Args:
            timeout: 超时时间，默认为60秒
            
        Returns:
            bool: 是否成功登录
        """
        logger.info(f"等待登录完成，最多等待 {timeout} 秒...")
        time_start = time.time()
        # 等待主界面元素出现
        while True:
            found, _, _ = self.controller.wait_for_image(template_name="login_success")
            if found:
                return  True
            found, _, _ = self.controller.wait_for_image(template_name="announcement")
            if found:
                return  True
            found, _, _ = self.controller.wait_for_image(template_name="daily_login")
            if found:
                return  True
            if time.time() - time_start > timeout:
                break
        
        logger.error("等待登录完成超时")
        return False

    def _handle_post_login_popups(self):
        """处理登录后可能出现的弹窗（公告、每日登录奖励等）"""
        logger.info("处理登录后的弹窗...")
        
        # 处理公告弹窗
        found, _, _ = self.controller.find_image(template_name="announcement")
        if found:
            logger.info("检测到公告弹窗，尝试关闭...")
            self.controller.tap_image(template_name="close_announcement")
            time.sleep(1)
        
        # 处理每日登录奖励
        found, _, _ = self.controller.find_image(template_name="daily_login")
        if found:
            logger.info("检测到每日登录奖励，尝试领取...")
            self.controller.tap(1510.1,929.0)
            time.sleep(1)
        
        # 等待屏幕稳定
        self.controller.wait_for_image(template_name="screen_stable")
        logger.info("登录后弹窗处理完成")
    
    def logout(self):
        """
        登出游戏
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("正在登出游戏...")
        
        # 关闭游戏
        if self.controller.stop_app(self.PACKAGE_NAME):
            logger.info("游戏已关闭")
            return True
        else:
            logger.error("关闭游戏失败")
            return False
    
    def restart_game(self, wait_time=30):
        """
        重启游戏
        
        Args:
            wait_time: 启动等待时间，默认为30秒
            
        Returns:
            bool: 重启是否成功
        """
        logger.info("正在重启游戏...")
        
        # 先关闭游戏
        self.logout()
        
        # 等待一段时间
        time.sleep(3)
        
        # 重新启动游戏
        return self.start_game(wait_time)

# 测试代码
if __name__ == "__main__":
    # 创建登录模块实例
    login_module = ArknightsLogin()
    
    # 连接到模拟器
    if login_module.connect():
        print("成功连接到模拟器")
        
        # 启动游戏
        if login_module.start_game():
            print("游戏启动成功")
            
            # 尝试登录
            if login_module.login():
                print("登录成功")
            else:
                print("登录失败")
        else:
            print("游戏启动失败")
    else:
        print("连接模拟器失败")
