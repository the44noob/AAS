#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模拟器连接模块
用于连接安卓模拟器并提供基本的ADB操作功能
"""

import os
import time
import logging
import subprocess
from ppadb.client import Client as AdbClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EmulatorController')

class EmulatorController:
    """模拟器控制器类，封装完整的模拟器操作流程"""

    def __init__(self, config):
        if not isinstance(config.get('emulator_path'), str) or not os.path.exists(config['emulator_path']):
            raise FileNotFoundError(f"模拟器路径不存在: {config['emulator_path']}")
        if not isinstance(config.get('adb_path'), str) or not os.path.exists(config['adb_path']):
            raise FileNotFoundError(f"ADB路径不存在: {config['adb_path']}")
        self.emulator_path = config['emulator_path']
        self.adb_path = config['adb_path']
        self.client = None
        self.device = None
        self.connected = False
        self.host = '127.0.0.1'
        self.port = config['device_port']

    def launch_emulator(self):
        """启动模拟器并建立ADB连接"""
        try:
            subprocess.Popen([self.emulator_path])
            print("雷电模拟器启动中...")
            max_wait = 120  # 最大等待时间120秒
            start_time = time.time()
            while time.time() - start_time < max_wait:
                if self._connect_adb():
                    return True
                time.sleep(5)
            return False
        except Exception as e:
            print(f"模拟器启动失败: {str(e)}")
            return False

    def _connect_adb(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', 5555)) != 0:
                print("模拟器端口未开放")
                return False
            subprocess.run([self.adb_path, 'kill-server'])
            result = subprocess.run(
                [self.adb_path, 'connect', '127.0.0.1:5555'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return 'connected' in result.stdout
        """
        初始化模拟器连接器
        
        Args:
            host: ADB服务器主机地址，默认为本地127.0.0.1
            port: ADB服务器端口，默认为5037
        """


    def execute_command(self, command):
        """
        执行ADB命令
        
        Args:
            command: 要执行的ADB命令
            
        Returns:
            str: 命令执行结果
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法执行命令")
            return ""
            
        try:
            result = self.device.shell(command)
            logger.debug(f"执行命令: {command}\n返回结果: {result}")
            return result
        except Exception as e:
            logger.error(f"执行命令 {command} 时出错: {str(e)}")
            return ""
    
    def connect(self, device_serial=None):
        """
        连接到模拟器
        
        Args:
            device_serial: 设备序列号，如果为None则连接到第一个可用设备
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 创建ADB客户端
            self.client = AdbClient()
            logger.info(f"ADB服务器版本: {self.client.version()}")
            
            # 获取设备列表
            devices = self.client.devices()
            if not devices:
                logger.error("未找到任何设备，请确保模拟器已启动")
                return False
            
            # 连接到指定设备或第一个可用设备
            if device_serial:
                for device in devices:
                    if device.serial == device_serial:
                        self.device = device
                        break
                if not self.device:
                    logger.error(f"未找到序列号为 {device_serial} 的设备")
                    return False
            else:
                self.device = devices[0]
            
            logger.info(f"已连接到设备: {self.device.serial}")
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"连接模拟器时出错: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开与模拟器的连接"""
        self.device = None
        self.connected = False
        logger.info("已断开与模拟器的连接")
    
    def is_connected(self):
        """
        检查是否已连接到模拟器
        
        Returns:
            bool: 是否已连接
        """
        return self.connected and self.device is not None
    
    def get_device_info(self):
        """
        获取设备信息
        
        Returns:
            dict: 设备信息字典
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法获取设备信息")
            return {}
        
        try:
            info = {
                "serial": self.device.serial,
                "android_version": self.device.shell("getprop ro.build.version.release").strip(),
                "device_model": self.device.shell("getprop ro.product.model").strip(),
                "screen_size": self.get_screen_size()
            }
            return info
        except Exception as e:
            logger.error(f"获取设备信息时出错: {str(e)}")
            return {}
    
    def get_screen_size(self):
        """
        获取屏幕尺寸
        
        Returns:
            tuple: (宽度, 高度)
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法获取屏幕尺寸")
            return (0, 0)
        
        try:
            output = self.device.shell("wm size").strip()
            # 解析输出，格式通常为 "Physical size: 1080x1920"
            size_str = output.split(": ")[1]
            width, height = map(int, size_str.split("x"))
            return (width, height)
        except Exception as e:
            logger.error(f"获取屏幕尺寸时出错: {str(e)}")
            return (0, 0)
    
    def take_screenshot(self, save_path=None):
        """
        截取屏幕截图
        
        Args:
            save_path: 保存截图的路径，如果为None则不保存到文件
            
        Returns:
            bytes: 截图数据
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法截取屏幕截图")
            return None
        
        for attempt in range(3):
            try:
                # 使用ADB截图并验证数据
                screenshot = self.device.screencap()
                if not screenshot or len(screenshot) < 1024:
                    raise ValueError("截图数据异常")
                
                # 转换为OpenCV格式进行二次验证
                # 暂时注释图像处理代码
                '''
                nparr = np.frombuffer(screenshot, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None or img.size == 0:
                    raise ValueError("OpenCV图像解码失败")
                '''
                
                # 如果指定了保存路径，则保存截图
                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(screenshot)
                    logger.info(f"截图已保存到: {save_path}")
                
                return screenshot
            except Exception as e:
                logger.warning(f"截图失败第{attempt+1}次尝试: {str(e)}")
                time.sleep(1)
        
        logger.error("截图失败，已达最大重试次数")
        return None
    
    def tap(self, x, y):
        """
        点击屏幕上的指定位置
        
        Args:
            x: 横坐标
            y: 纵坐标
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法执行点击操作")
            return False
        
        try:
            self.device.shell(f"input tap {x} {y}")
            logger.debug(f"点击位置: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"点击屏幕时出错: {str(e)}")
            return False
    
    def swipe(self, start_x, start_y, end_x, end_y, duration=300):
        """
        在屏幕上滑动
        
        Args:
            start_x: 起始点横坐标
            start_y: 起始点纵坐标
            end_x: 结束点横坐标
            end_y: 结束点纵坐标
            duration: 滑动持续时间(毫秒)
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法执行滑动操作")
            return False
        
        try:
            self.device.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
            logger.debug(f"滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y}), 持续时间: {duration}ms")
            return True
        except Exception as e:
            logger.error(f"滑动屏幕时出错: {str(e)}")
            return False
    
    def input_text(self, text):
        """
        输入文本
        
        Args:
            text: 要输入的文本
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法执行文本输入操作")
            return False
        
        try:
            # 对特殊字符进行转义
            escaped_text = text.replace(" ", "%s").replace("'", "\\'").replace("\"", "\\\"")
            self.device.shell(f"input text '{escaped_text}'")
            logger.debug(f"输入文本: {text}")
            return True
        except Exception as e:
            logger.error(f"输入文本时出错: {str(e)}")
            return False
    
    def press_key(self, keycode):
        """
        按下按键
        
        Args:
            keycode: 按键代码，参考Android KeyEvent
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法执行按键操作")
            return False
        
        try:
            self.device.shell(f"input keyevent {keycode}")
            logger.debug(f"按下按键: {keycode}")
            return True
        except Exception as e:
            logger.error(f"按下按键时出错: {str(e)}")
            return False
    
    def start_app(self, package_name):
        """
        启动应用
        
        Args:
            package_name: 应用包名
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法启动应用")
            return False
        
        try:
            # 使用monkey命令启动应用
            result = self.device.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
            if "No activities found" in result:
                logger.error(f"未找到应用: {package_name}")
                return False
            
            logger.info(f"已启动应用: {package_name}")
            return True
        except Exception as e:
            logger.error(f"启动应用时出错: {str(e)}")
            return False
    
    def stop_app(self, package_name):
        """
        停止应用
        
        Args:
            package_name: 应用包名
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            logger.error("未连接到模拟器，无法停止应用")
            return False
        
        try:
            self.device.shell(f"am force-stop {package_name}")
            logger.info(f"已停止应用: {package_name}")
            return True
        except Exception as e:
            logger.error(f"停止应用时出错: {str(e)}")
            return False

# 测试代码
if __name__ == "__main__":
    # 创建模拟器连接器实例
    config = {
        'emulator_path': 'Z:\\leidian\\LDPlayer9\\dnplayer.exe',
        'adb_path': 'Z:\\leidian\\LDPlayer9\\adb.exe'
    }
    connector = EmulatorController(config)
    
    # 连接到模拟器
    if connector.connect():
        print("成功连接到模拟器")
        
        # 获取设备信息
        device_info = connector.get_device_info()
        print(f"设备信息: {device_info}")
        
        # 截取屏幕截图
        screenshot_path = "screenshot.png"
        connector.take_screenshot(screenshot_path)
        print(f"截图已保存到: {screenshot_path}")
        
        # 断开连接
        connector.disconnect()
    else:
        print("连接模拟器失败")
