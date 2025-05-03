#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
明日方舟基建收菜模块
负责执行基建收菜相关操作
"""

import os
import time
import logging
import random
from .game_controller import GameController

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ArknightsBase')

class ArknightsBase:
    """明日方舟基建类，负责执行基建收菜相关操作"""
    
    # 基建相关界面元素模板
    TEMPLATES = {
        "base_icon": "base_icon.png",                # 主界面基建图标
        "enter_base": "enter_base.png",              # 进入基建按钮?
        "notification": "notification.png",          # 基建通知图标
        "collect_all": "collect_all.png",            # 全部收取按钮
        "trust_tap": "trust_tap.png",                # 信赖点击提示
        "factory": "factory.png",                    # 制造站图标
        "trading_post": "trading_post.png",          # 贸易站图标
        "dormitory": "dormitory.png",                # 宿舍图标
        "control_center": "control_center.png",      # 控制中枢图标
        "confirm_collect": "confirm_collect.png",    # 确认收取按钮
        "back_button": "back_button.png",            # 返回按钮
        "drone": "drone.png",                        # 无人机图标
        "use_drone": "use_drone.png",                # 使用无人机按钮
        "max_drone": "max_drone.png",                # 最大无人机数量按钮
        "confirm_drone": "confirm_drone.png",        # 确认使用无人机按钮
        "order_complete": "order_complete.png",      # 订单完成图标
        "collect_order": "collect_order.png",        # 收取订单按钮
        "new_order": "new_order.png",                # 新订单按钮
        "select_order": "select_order.png",          # 选择订单按钮
        "confirm_order": "confirm_order.png",        # 确认订单按钮
        "tired_operator": "tired_operator.png",      # 疲劳干员图标
        "overview": "overview.png",                  # 进驻总览图标
        "replace_operator": "replace_operator.png",  # 更换干员按钮
        "clear_selection": "clear_selection.png",    # 清空选择按钮
        "auto_select": "auto_select.png",            # 自动选择按钮
        "confirm_replace": "confirm_replace.png",    # 确认更换按钮
        "confirm_quit": "confirm_quit.png",    # 确认更换按钮
    }
    
    # 基建设施坐标（根据实际情况调整）
    FACILITY_POSITIONS = {
        "control_center": (500, 400),
        "trading_post_1": (300, 300),
        "trading_post_2": (300, 500),
        "factory_1": (700, 300),
        "factory_2": (700, 400),
        "factory_3": (700, 500),
        "dormitory_1": (200, 200),
        "dormitory_2": (400, 200),
        "dormitory_3": (600, 200),
        "dormitory_4": (800, 200),
    }
    
    def __init__(self, controller=None, template_dir=None):
        """
        初始化明日方舟基建模块
        
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
        
        logger.info("明日方舟基建模块初始化完成")
    
    def _load_templates(self):
        """加载基建相关的模板图像"""
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
    
    def navigate_to_base(self):
        """
        导航到基建界面
        
        Returns:
            bool: 是否成功导航到基建界面
        """
        logger.info("正在导航到基建界面...")
        
        # 确保在主界面
        # 可以添加检查主界面的代码，如果不在主界面则返回主界面
        
        # 点击基建图标
        if not self.controller.tap_image(template_name="base_icon", max_retries=3):
            logger.error("未找到基建图标")
            return False
        
        # 等待基建界面加载
        time.sleep(3)
        
        # 检查是否成功进入基建界面
        self.controller.take_screenshot()
        found, _, _ = self.controller.find_image(template_name="overview")
        
        if found:
            logger.info("已成功进入基建界面")
            return True
        else:
            logger.error("导航到基建界面失败")
            return False
    
    def collect_all_resources(self):
        """
        收取所有资源
        
        Returns:
            bool: 是否成功收取所有资源
        """
        logger.info("正在收取所有资源...")
        
        # 点击进入基建按钮
        if not self.controller.tap_image(template_name="notification", max_retries=3):
            logger.error("未找到消息按钮")
            return False
        
        for i in range(3):
            # 点击全部收取按钮
            if not self.controller.tap(367.7,1044.0):
                logger.error("未找到全部收取按钮")
                return False
            # 等待收取动画
            time.sleep(2)
            # 处理可能出现的确认收取弹窗
            self.controller.tap_image(template_name="confirm_collect")
        if not self.controller.find_image(template_name="overview"):
            # 返回基建主界面
            self.controller.tap_image(template_name="back_button")
            time.sleep(2)
        logger.info("已收取所有资源")
        return True
    
    def visit_trading_posts(self):
        """
        访问所有贸易站，收取订单并创建新订单
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("正在访问贸易站...")
        
        # 访问每个贸易站
        for name, position in self.FACILITY_POSITIONS.items():
            if "trading_post" in name:
                logger.info(f"访问 {name}...")
                
                # 点击贸易站
                self.controller.tap(position[0], position[1])
                time.sleep(2)
                
                # 检查是否有完成的订单
                found, _, _ = self.controller.find_image(template_name="order_complete")
                if found:
                    # 收取订单
                    self.controller.tap_image(template_name="collect_order")
                    time.sleep(1)
                
                # 检查是否可以创建新订单
                found, _, _ = self.controller.find_image(template_name="new_order")
                if found:
                    # 创建新订单
                    self.controller.tap_image(template_name="new_order")
                    time.sleep(1)
                    
                    # 选择订单
                    self.controller.tap_image(template_name="select_order")
                    time.sleep(1)
                    
                    # 确认订单
                    self.controller.tap_image(template_name="confirm_order")
                    time.sleep(1)
                
                # 使用无人机加速（可选）
                self._use_drones_if_available()
                
                # 返回基建主界面
                self.controller.tap_image(template_name="back_button")
                time.sleep(2)
        
        logger.info("贸易站访问完成")
        return True
    
    def visit_factories(self):
        """
        访问所有制造站，收取产品并开始新的生产
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("正在访问制造站...")
        
        # 访问每个制造站
        for name, position in self.FACILITY_POSITIONS.items():
            if "factory" in name:
                logger.info(f"访问 {name}...")
                
                # 点击制造站
                self.controller.tap(position[0], position[1])
                time.sleep(2)
                
                # 收取产品（点击屏幕中央）
                self.controller.tap(500, 400)
                time.sleep(1)
                
                # 如果生产已停止，重新开始生产
                # 这里需要根据实际界面添加更多逻辑
                
                # 使用无人机加速（可选）
                self._use_drones_if_available()
                
                # 返回基建主界面
                self.controller.tap_image(template_name="back_button")
                time.sleep(2)
        
        logger.info("制造站访问完成")
        return True
    
    def _use_drones_if_available(self):
        """
        如果有无人机可用，则使用无人机加速
        
        Returns:
            bool: 是否成功使用无人机
        """
        # 检查是否有无人机按钮
        found, _, _ = self.controller.find_image(template_name="drone")
        if not found:
            return False
        
        # 点击无人机按钮
        self.controller.tap_image(template_name="drone")
        time.sleep(1)
        
        # 点击使用无人机按钮
        self.controller.tap_image(template_name="use_drone")
        time.sleep(1)
        
        # 点击最大数量
        self.controller.tap_image(template_name="max_drone")
        time.sleep(1)
        
        # 确认使用
        self.controller.tap_image(template_name="confirm_drone")
        time.sleep(2)
        
        logger.info("已使用无人机加速")
        return True
    
    def check_and_replace_tired_operators(self):
        """
        检查并更换疲劳干员
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("正在检查疲劳干员...")
        
        # 访问每个设施
        #for name, position in self.FACILITY_POSITIONS.items():
        #    # 跳过宿舍
        #    if "dormitory" in name:
        #        continue
        #    
        #    logger.info(f"检查 {name} 的干员状态...")
        #    
        #    # 点击设施
        #    self.controller.tap(position[0], position[1])
        #    time.sleep(2)
        #    
        #    # 检查是否有疲劳干员
        #    found, _, _ = self.controller.find_image(template_name="tired_operator")
        #    if found:
        #        logger.info(f"在 {name} 中发现疲劳干员，准备更换...")
        #        
        #        # 点击更换干员按钮
        #        if self.controller.tap_image(template_name="replace_operator"):
        #            time.sleep(1)
        #            
        #            # 清空当前选择
        #            self.controller.tap_image(template_name="clear_selection")
        #            time.sleep(1)
        #            
        #            # 使用自动选择
        #            self.controller.tap_image(template_name="auto_select")
        #            time.sleep(1)
        #            
        #            # 确认更换
        #            self.controller.tap_image(template_name="confirm_replace")
        #            time.sleep(2)
        self.controller.tap_image(template_name="overview")
        self.controller.tap(1753.0,1009.0)    
        # 返回基建主界面
        self.controller.tap_image(template_name="back_button")
        time.sleep(2)
        
        logger.info("干员检查和更换完成")
        return True
    
    def visit_dormitories(self):
        """
        访问宿舍，收取信赖
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("正在访问宿舍...")
        
        # 访问每个宿舍
        for name, position in self.FACILITY_POSITIONS.items():
            if "dormitory" in name:
                logger.info(f"访问 {name}...")
                
                # 点击宿舍
                self.controller.tap(position[0], position[1])
                time.sleep(2)
                
                # 点击屏幕中央收取信赖
                self.controller.tap(500, 400)
                time.sleep(1)
                
                # 处理信赖点击
                for _ in range(5):  # 尝试点击几次
                    found, position, _ = self.controller.find_image(template_name="trust_tap")
                    if found:
                        self.controller.tap(position[0], position[1])
                        time.sleep(0.5)
                    else:
                        break
                
                # 返回基建主界面
                self.controller.tap_image(template_name="back_button")
                time.sleep(2)
        
        logger.info("宿舍访问完成")
        return True
    
    def visit_control_center(self):
        """
        访问控制中枢，收取信赖
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("正在访问控制中枢...")
        
        # 点击控制中枢
        position = self.FACILITY_POSITIONS.get("control_center")
        if position:
            self.controller.tap(position[0], position[1])
            time.sleep(2)
            
            # 点击屏幕中央收取信赖
            self.controller.tap(500, 400)
            time.sleep(1)
            
            # 处理信赖点击
            for _ in range(5):  # 尝试点击几次
                found, position, _ = self.controller.find_image(template_name="trust_tap")
                if found:
                    self.controller.tap(position[0], position[1])
                    time.sleep(0.5)
                else:
                    break
            
            # 返回基建主界面
            self.controller.tap_image(template_name="back_button")
            time.sleep(2)
        
        logger.info("控制中枢访问完成")
        return True
    
    def return_to_main(self):
        """
        返回主界面
        
        Returns:
            bool: 是否成功返回主界面
        """
        logger.info("正在返回主界面...")
        
        # 点击返回按钮，可能需要点击多次
        for _ in range(3):
            if self.controller.tap_image(template_name="confirm_quit"):
                time.sleep(1)
            if self.controller.tap_image(template_name="back_button"):
                time.sleep(1)
            else:
                break
        
        logger.info("已返回主界面")
        return True
    
    def execute_base_collection(self):
        """
        执行完整的基建收菜流程
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始执行基建收菜流程...")
        
        # 导航到基建界面
        if not self.navigate_to_base():
            return False
        
         # 检查并更换疲劳干员
        self.check_and_replace_tired_operators()

        # 收取所有资源
        self.collect_all_resources()
        
        ## 访问贸易站
        #self.visit_trading_posts()
        #
        ## 访问制造站
        #self.visit_factories()
        #
        ## 访问宿舍
        #self.visit_dormitories()
        #
        ## 访问控制中枢
        #self.visit_control_center()
        
        # 返回主界面
        self.return_to_main()
        
        logger.info("基建收菜流程执行完成")
        return True

# 测试代码
if __name__ == "__main__":
    # 创建基建模块实例
    base = ArknightsBase()
    
    # 连接到模拟器
    if base.controller.connect_emulator():
        print("成功连接到模拟器")
        
        # 执行基建收菜流程
        if base.execute_base_collection():
            print("基建收菜流程执行成功")
        else:
            print("基建收菜流程执行失败")
    else:
        print("连接模拟器失败")
