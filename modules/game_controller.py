#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户交互模块
整合模拟器连接和图像识别功能，提供高级游戏操作接口
"""

import os
import time
import random
import logging
from .emulator import EmulatorController
from .image_recognition import ImageRecognizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GameController')

class GameController:
    """游戏控制器类，提供基于图像识别的游戏操作功能"""
    
    def __init__(self, emulator=None, recognizer=None, screenshot_dir="screenshots"):
        """
        初始化游戏控制器
        
        Args:
            emulator: EmulatorController实例，如果为None则创建新实例
            recognizer: ImageRecognizer实例，如果为None则创建新实例
            screenshot_dir: 截图保存目录，默认为"screenshots"
        """
        # 初始化模拟器连接器
        self.emulator = emulator if emulator else EmulatorController()
        
        # 初始化图像识别器
        self.recognizer = recognizer if recognizer else ImageRecognizer()
        
        # 截图保存目录
        self.screenshot_dir = screenshot_dir
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        # 最新截图
        self.current_screenshot = None
        self.screenshot_path = None
        
        logger.info("游戏控制器初始化完成")
    
    def connect_emulator(self, device_serial=None):
        """
        连接到模拟器
        
        Args:
            device_serial: 设备序列号，如果为None则连接到第一个可用设备
            
        Returns:
            bool: 连接是否成功
        """
        return self.emulator.connect(device_serial)
    
    def start_app(self, package_name, wait_time=5):
        """
        启动应用程序
        
        Args:
            package_name: 应用程序包名
            wait_time: 启动等待时间，默认为5秒
            
        Returns:
            bool: 启动是否成功
        """
        if not self.emulator.is_connected():
            logger.error("未连接到模拟器，无法启动应用")
            return False
        
        try:
            logger.info(f"正在启动应用: {package_name}")
            
            # 使用ADB启动应用
            result = self.emulator.start_app(package_name)
            
            if not result:
                logger.error(f"启动应用失败: {result}")
                return False
            
            # 等待应用启动
            if wait_time > 0:
                logger.info(f"等待应用启动，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            
            logger.info(f"应用已启动: {package_name}")
            return True
        except Exception as e:
            logger.error(f"启动应用时出错: {str(e)}")
            return False
    
    def stop_app(self, package_name):
        """
        停止应用程序
        
        Args:
            package_name: 应用程序包名
            
        Returns:
            bool: 停止是否成功
        """
        if not self.emulator.is_connected():
            logger.error("未连接到模拟器，无法停止应用")
            return False
        
        try:
            logger.info(f"正在停止应用: {package_name}")
            
            # 使用ADB停止应用
            result = self.emulator.execute_command(f"shell am force-stop {package_name}")
            
            if result and "Error" in result:
                logger.error(f"停止应用失败: {result}")
                return False
            
            logger.info(f"应用已停止: {package_name}")
            return True
        except Exception as e:
            logger.error(f"停止应用时出错: {str(e)}")
            return False
    
    def take_screenshot(self, save=True, filename=None):
        """
        截取屏幕截图
        
        Args:
            save: 是否保存截图，默认为True
            filename: 保存的文件名，如果为None则使用时间戳
            
        Returns:
            bytes: 截图数据
        """
        if not self.emulator.is_connected():
            logger.error("未连接到模拟器，无法截取屏幕截图")
            return None
        
        try:
            # 生成文件名
            if save:
                if filename is None:
                    filename = f"screenshot_{int(time.time())}.png"
                self.screenshot_path = os.path.join(self.screenshot_dir, filename)
            else:
                self.screenshot_path = None
            
            # 截取屏幕截图
            self.current_screenshot = self.emulator.take_screenshot(self.screenshot_path)
            return self.current_screenshot
        except Exception as e:
            logger.error(f"截取屏幕截图时出错: {str(e)}")
            return None
    
    def find_image(self, template_name=None, template_path=None, threshold=0.8, region=None, take_new_screenshot=True):
        """
        在屏幕上查找图像
        
        Args:
            template_name: 模板名称，如果提供则使用已加载的模板
            template_path: 模板图像路径，如果template_name为None则使用此参数
            threshold: 匹配阈值，默认为0.8
            region: 搜索区域 (x, y, width, height)，如果为None则搜索整个屏幕
            take_new_screenshot: 是否重新截图，默认为True
            
        Returns:
            tuple: (是否找到, 位置(x, y), 匹配得分)
        """
        # 获取截图
        if take_new_screenshot or self.current_screenshot is None:
            self.take_screenshot()
        
        if self.current_screenshot is None:
            logger.error("没有可用的截图")
            return False, (0, 0), 0.0
        
        try:
            # 如果指定了搜索区域，则裁剪图像
            if region:
                x, y, width, height = region
                img = self.recognizer.crop_image(self.current_screenshot, x, y, width, height)
                if img is None:
                    logger.error("裁剪图像失败")
                    return False, (0, 0), 0.0
            else:
                img = self.screenshot_path
            
            # 如果提供了模板路径而不是模板名称，则加载模板
            print(img)
            if template_name is None and template_path is not None:
                if not os.path.isfile(template_path):
                    logger.error(f"模板文件不存在: {template_path}")
                    return False, (0, 0), 0.0
                
                # 执行模板匹配
                success, position, score = self.recognizer.match_template(img, template=template_path, threshold=threshold)
            else:
                # 使用已加载的模板
                success, position, score = self.recognizer.match_template(img, template_name=template_name, threshold=threshold)
            
            # 如果使用了裁剪区域，需要调整坐标
            if region and success:
                position = (position[0] + region[0], position[1] + region[1])
            
            return success, position, score
        except Exception as e:
            logger.error(f"查找图像时出错: {str(e)}")
            return False, (0, 0), 0.0
    
    def find_all_images(self, image,template_name=None, template_path=None, threshold=0.8, region=None, max_results=10, take_new_screenshot=True):
        """
        在屏幕上查找所有匹配的图像
        
        Args:
            template_name: 模板名称，如果提供则使用已加载的模板
            template_path: 模板图像路径，如果template_name为None则使用此参数
            threshold: 匹配阈值，默认为0.8
            region: 搜索区域 (x, y, width, height)，如果为None则搜索整个屏幕
            max_results: 最大结果数量，默认为10
            take_new_screenshot: 是否重新截图，默认为True
            
        Returns:
            list: 匹配结果列表，每个元素为 (位置(x, y), 得分)
        """
        ## 获取截图
        #if take_new_screenshot or self.current_screenshot is None:
        #    self.take_screenshot()
        #
        #if self.current_screenshot is None:
        #    logger.error("没有可用的截图")
        #    return []
        #
        #try:
        #    # 如果指定了搜索区域，则裁剪图像
        #    if region:
        #        x, y, width, height = region
        #        img = self.recognizer.crop_image(self.current_screenshot, x, y, width, height)
        #        if img is None:
        #            logger.error("裁剪图像失败")
        #            return []
        #    else:
        #        img = self.current_screenshot
        #    
        #    # 如果提供了模板路径而不是模板名称，则加载模板
        #    if template_name is None and template_path is not None:
        #        if not os.path.isfile(template_path):
        #            logger.error(f"模板文件不存在: {template_path}")
        #            return []
        #        
        #        # 查找所有匹配
        #        matches = self.recognizer.find_all_matches(img, template=template_path, threshold=threshold, max_results=max_results)
        #    else:
        #        # 使用已加载的模板
        #        matches = self.recognizer.find_all_matches(img, template_name=template_name, threshold=threshold, max_results=max_results)
        #    
        #    # 如果使用了裁剪区域，需要调整坐标
        #    if region and matches:
        #        matches = [((pos[0] + region[0], pos[1] + region[1]), score) for pos, score in matches]
        #    
        #    return matches
        #except Exception as e:
        #    logger.error(f"查找所有图像时出错: {str(e)}")
        #    return []
        return self.recognizer.find_all_matches(image=image, template_name=template_name, template=template_path, threshold=threshold, max_results=max_results)
    
    def tap(self, x, y, random_offset=10, sleep_after=0.5):
        """
        点击屏幕上的指定位置
        
        Args:
            x: 横坐标
            y: 纵坐标
            random_offset: 随机偏移量，默认为10像素
            sleep_after: 点击后等待时间，默认为0.5秒
            
        Returns:
            bool: 操作是否成功
        """
        if not self.emulator.is_connected():
            logger.error("未连接到模拟器，无法执行点击操作")
            return False
        
        try:
            # 添加随机偏移，模拟真实点击
            if random_offset > 0:
                x += random.randint(-random_offset, random_offset)
                y += random.randint(-random_offset, random_offset)
            
            # 执行点击
            result = self.emulator.tap(x, y)
            
            # 等待
            if sleep_after > 0:
                time.sleep(sleep_after)
            
            return result
        except Exception as e:
            logger.error(f"点击屏幕时出错: {str(e)}")
            return False
    
    def tap_image(self, template_name=None, template_path=None, threshold=0.8, region=None, random_offset=10, sleep_after=0.5, max_retries=3):
        """
        查找并点击图像
        
        Args:
            template_name: 模板名称，如果提供则使用已加载的模板
            template_path: 模板图像路径，如果template_name为None则使用此参数
            threshold: 匹配阈值，默认为0.8
            region: 搜索区域 (x, y, width, height)，如果为None则搜索整个屏幕
            random_offset: 随机偏移量，默认为10像素
            sleep_after: 点击后等待时间，默认为0.5秒
            max_retries: 最大重试次数，默认为3
            
        Returns:
            bool: 操作是否成功
        """
        for i in range(max_retries):
            # 查找图像
            found, position, score = self.find_image(template_name, template_path, threshold, region)
            
            if found:
                # 点击找到的位置
                logger.info(f"找到图像，位置: {position}, 得分: {score:.4f}, 正在点击...")
                return self.tap(position[0], position[1], random_offset, sleep_after)
            
            # 如果没找到，等待一段时间后重试
            if i < max_retries - 1:
                logger.debug(f"未找到图像，{i+1}/{max_retries} 次尝试，等待后重试...")
                time.sleep(1)
        
        logger.warning(f"在 {max_retries} 次尝试后未找到图像")
        return False
    
    def swipe(self, start_x, start_y, end_x, end_y, duration=300, sleep_after=0.5):
        """
        在屏幕上滑动
        
        Args:
            start_x: 起始点横坐标
            start_y: 起始点纵坐标
            end_x: 结束点横坐标
            end_y: 结束点纵坐标
            duration: 滑动持续时间(毫秒)，默认为300
            sleep_after: 滑动后等待时间，默认为0.5秒
            
        Returns:
            bool: 操作是否成功
        """
        if not self.emulator.is_connected():
            logger.error("未连接到模拟器，无法执行滑动操作")
            return False
        
        try:
            # 执行滑动
            result = self.emulator.swipe(start_x, start_y, end_x, end_y, duration)
            
            # 等待
            if sleep_after > 0:
                time.sleep(sleep_after)
            
            return result
        except Exception as e:
            logger.error(f"滑动屏幕时出错: {str(e)}")
            return False
    
    def wait_for_image(self, template_name=None, template_path=None, threshold=0.8, region=None, timeout=30, interval=1.0):
        """
        等待图像出现
        
        Args:
            template_name: 模板名称，如果提供则使用已加载的模板
            template_path: 模板图像路径，如果template_name为None则使用此参数
            threshold: 匹配阈值，默认为0.8
            region: 搜索区域 (x, y, width, height)，如果为None则搜索整个屏幕
            timeout: 超时时间(秒)，默认为30秒
            interval: 检查间隔(秒)，默认为1秒
            
        Returns:
            tuple: (是否找到, 位置(x, y), 匹配得分)
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 查找图像
            found, position, score = self.find_image(template_name, template_path, threshold, region)
            
            if found:
                logger.info(f"找到图像，位置: {position}, 得分: {score:.4f}")
                return True, position, score
            
            # 等待一段时间后重试
            time.sleep(interval)
        
        logger.warning(f"在 {timeout} 秒内未找到图像")
        return False, (0, 0), 0.0
    
    def wait_and_tap_image(self, template_name=None, template_path=None, threshold=0.8, region=None, timeout=30, interval=1.0, random_offset=10, sleep_after=0.5):
        """
        等待图像出现并点击
        
        Args:
            template_name: 模板名称，如果提供则使用已加载的模板
            template_path: 模板图像路径，如果template_name为None则使用此参数
            threshold: 匹配阈值，默认为0.8
            region: 搜索区域 (x, y, width, height)，如果为None则搜索整个屏幕
            timeout: 超时时间(秒)，默认为30秒
            interval: 检查间隔(秒)，默认为1秒
            random_offset: 随机偏移量，默认为10像素
            sleep_after: 点击后等待时间，默认为0.5秒
            
        Returns:
            bool: 操作是否成功
        """
        # 等待图像出现
        found, position, score = self.wait_for_image(template_name, template_path, threshold, region, timeout, interval)
        
        if found:
            # 点击找到的位置
            return self.tap(position[0], position[1], random_offset, sleep_after)
        
        return False
    
    def wait_for_any_image(self, templates, threshold=0.8, region=None, timeout=30, interval=1.0):
        """
        等待任意一个图像出现
        
        Args:
            templates: 模板列表，每个元素为 (template_name, template_path)，其中一个可以为None
            threshold: 匹配阈值，默认为0.8
            region: 搜索区域 (x, y, width, height)，如果为None则搜索整个屏幕
            timeout: 超时时间(秒)，默认为30秒
            interval: 检查间隔(秒)，默认为1秒
            
        Returns:
            tuple: (模板索引, 是否找到, 位置(x, y), 匹配得分)
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 获取新截图
            self.take_screenshot()
            
            # 检查每个模板
            for i, (template_name, template_path) in enumerate(templates):
                found, position, score = self.find_image(template_name, template_path, threshold, region, take_new_screenshot=False)
                
                if found:
                    logger.info(f"找到图像 {i}，位置: {position}, 得分: {score:.4f}")
                    return i, True, position, score
            
            # 等待一段时间后重试
            time.sleep(interval)
        
        logger.warning(f"在 {timeout} 秒内未找到任何图像")
        return -1, False, (0, 0), 0.0
    
    def wait_and_tap_any_image(self, templates, threshold=0.8, region=None, timeout=30, interval=1.0, random_offset=10, sleep_after=0.5):
        """
        等待任意一个图像出现并点击
        
        Args:
            templates: 模板列表，每个元素为 (template_name, template_path)，其中一个可以为None
            threshold: 匹配阈值，默认为0.8
            region: 搜索区域 (x, y, width, height)，如果为None则搜索整个屏幕
            timeout: 超时时间(秒)，默认为30秒
            interval: 检查间隔(秒)，默认为1秒
            random_offset: 随机偏移量，默认为10像素
            sleep_after: 点击后等待时间，默认为0.5秒
            
        Returns:
            tuple: (模板索引, 操作是否成功)
        """
        # 等待任意图像出现
        index, found, position, score = self.wait_for_any_image(templates, threshold, region, timeout, interval)
        
        if found:
            # 点击找到的位置
            success = self.tap(position[0], position[1], random_offset, sleep_after)
            return index, success
        
        return -1, False
    
    def check_color(self, x, y, expected_color, tolerance=10, take_new_screenshot=True):
        """
        检查指定位置的颜色
    
(Content truncated due to size limit. Use line ranges to read in chunks) """