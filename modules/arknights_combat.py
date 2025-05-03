#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
明日方舟作战模块
负责执行上一次作战相关操作
"""

import os
import time
import logging
from .game_controller import GameController

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ArknightsCombat')

class ArknightsCombat:
    """明日方舟作战类，负责执行上一次作战相关操作"""
    
    # 作战相关界面元素模板
    TEMPLATES = {
        "combat_icon": "combat_icon.png",            # 主界面作战图标
        "last_combat": "last_combat.png",            # 上一次作战按钮
        "start_combat": "start_combat.png",          # 开始行动按钮
        "combat_times": "combat_times.png",          # 行动次数按钮
        "6_multiple": "6_multiple.png",          # 行动次数按钮
        "5_multiple": "5_multiple.png",          # 行动次数按钮
        "4_multiple": "4_multiple.png",          # 行动次数按钮
        "3_multiple": "3_multiple.png",          # 行动次数按钮
        "2_multiple": "2_multiple.png",          # 行动次数按钮
        "1_multiple": "1_multiple.png",          # 行动次数按钮

        "confirm_team": "confirm_team.png",          # 确认队伍按钮
        "combat_start": "combat_start.png",          # 战斗开始标志
        "combat_finish": "combat_finish.png",        # 战斗结束标志
        "combat_success": "combat_success.png",      # 战斗成功标志
        "combat_failure": "combat_failure.png",      # 战斗失败标志
        "level_up": "level_up.png",                  # 等级提升标志
        "confirm_result": "confirm_result.png",      # 确认结果按钮?
        "sanity_refill": "sanity_refill.png",        # 理智补充弹窗
        "use_originite": "use_originite.png",        # 使用源石按钮
        "use_potion": "use_potion.png",              # 使用药剂按钮
        "already_potion": "already_potion.png",      # 使用药剂按钮
        "confirm_refill": "confirm_refill.png",      # 确认补充按钮
        "cancel_refill": "cancel_refill.png",        # 取消补充按钮
        "auto_deploy": "auto_deploy.png",            # 自动部署开关
        "back_button": "back_button.png",            # 返回按钮
    }
    
    def __init__(self, controller=None, template_dir=None):
        """
        初始化明日方舟作战模块
        
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
        
        logger.info("明日方舟作战模块初始化完成")
    
    def _load_templates(self):
        """加载作战相关的模板图像"""
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
    
    def navigate_to_combat(self):
        """
        导航到作战界面
        
        Returns:
            bool: 是否成功导航到作战界面
        """
        logger.info("正在导航到作战界面...")
        
        # 确保在主界面
        # 可以添加检查主界面的代码，如果不在主界面则返回主界面
        
        # 点击作战图标
        if not self.controller.tap_image(template_name="combat_icon", max_retries=3):
            logger.error("未找到作战图标")
            return False
        
        # 等待作战界面加载
        time.sleep(3)
        
        logger.info("已成功进入作战界面")
        return True
    
    def start_last_combat(self, use_sanity_item=False, max_times=1):
        """
        开始上一次作战
        
        Args:
            use_sanity_item: 是否使用理智药剂，默认为False
            max_times: 最大作战次数，默认为1
            
        Returns:
            int: 成功完成的作战次数
        """
        logger.info(f"开始执行上一次作战，计划次数: {max_times}...")
        
        # 点击上一次作战按钮
        if not self.controller.tap_image(template_name="last_combat", max_retries=3):
            logger.error("未找到上一次作战按钮")
            return 0
        # 检查并确保自动部署已开启
        self.check_auto_deploy()
        # 等待界面加载
        time.sleep(2)
        
        
        self.controller.tap(1447.1,888.2)
        self.controller.tap_image("6_multiple")
        completed_times = 0
        index = 5
        for i in range(max_times):
            logger.info(f"开始第 {i+1}/{max_times} 次作战...")
            
            # 点击开始行动按钮
            if not self.controller.tap_image(template_name="start_combat", max_retries=3):
                logger.error("未找到开始行动按钮")
                break
            
            # 等待界面加载
            time.sleep(2)
            
            # 处理理智不足情况
            if self._handle_sanity_refill(use_sanity_item):
                # 如果理智补充成功或不需要补充，继续作战
                pass
            else:
                for j in range (5):
                    self.controller.tap(1447.1,888.2)
                    time.sleep(1)
                    self.controller.tap_image(str(index)+"_multiple")
                    index = index - 1
                    self.controller.tap_image(template_name="start_combat")
                    if self._handle_sanity_refill(use_sanity_item):
                        break
            if index > 0:
                self.controller.tap_image(template_name="start_combat", max_retries=3)
                pass
            else:
                # 如果理智不足且不使用药剂，则退出
                logger.warning("理智不足且不使用药剂，停止作战")
                break
            # 确认队伍
            if not self.controller.tap_image(template_name="confirm_team", max_retries=3):
                logger.error("未找到确认队伍按钮")
                break
            
            # 等待战斗开始
            found, _, _ = self.controller.wait_for_image(template_name="combat_start", timeout=30)
            if not found:
                logger.error("等待战斗开始超时")
                break
            
            # 等待战斗结束
            success = self._wait_for_combat_finish()
            if success:
                completed_times += 1
                logger.info(f"第 {i+1} 次作战完成")
            else:
                logger.error(f"第 {i+1} 次作战失败或超时")
                break
            
            # 如果已经完成所有计划的作战，退出循环
            if completed_times >= max_times:
                break
            
            # 等待界面恢复
            time.sleep(3)
        
        logger.info(f"共完成 {completed_times}/{max_times} 次作战")
        return completed_times
    
    def _handle_sanity_refill(self, use_sanity_item=False):
        """
        处理理智补充
        
        Args:
            use_sanity_item: 是否使用理智药剂，默认为False
            
        Returns:
            bool: 是否成功处理理智问题（补充成功或不需要补充）
        """
        # 检查是否出现理智补充弹窗
        found, _, _ = self.controller.find_image(template_name="sanity_refill")
        
        if not found:
            # 没有出现理智补充弹窗，说明理智充足
            return True
        
        logger.info("检测到理智不足弹窗")
        
        if not use_sanity_item:
            # 不使用理智药剂，点击取消
            logger.info("设置为不使用理智药剂，取消补充")
            self.controller.tap_image(template_name="cancel_refill")
            return False
        
        # 使用理智药剂
        logger.info("尝试使用理智药剂")
        
        # 优先使用药剂而不是源石
        if self.controller.tap_image(template_name="use_potion") or self.controller.find_image(template_name="already_potion"):
            # 点击确认补充按钮
            time.sleep(1)
            if self.controller.tap_image(template_name="confirm_refill"):
                logger.info("已使用理智药剂")
                time.sleep(2)
                return True
        
        # 如果没有药剂，检查是否要使用源石
        # 这里默认不使用源石，可以根据需要修改
        logger.warning("没有理智药剂或使用失败")
        self.controller.tap_image(template_name="cancel_refill")
        return False
    
    def _wait_for_combat_finish(self, timeout=300):
        """
        等待战斗结束
        
        Args:
            timeout: 超时时间，默认为300秒（5分钟）
            
        Returns:
            bool: 战斗是否成功完成
        """
        logger.info(f"等待战斗结束，最多等待 {timeout} 秒...")
        
        start_time = time.time()
        success = False
        
        while time.time() - start_time < timeout:
            # 截图检查
            self.controller.take_screenshot()
            
            # 检查是否战斗成功
            found, _, _ = self.controller.find_image(template_name="combat_success")
            if found:
                logger.info("检测到战斗成功")
                success = True
                break
            
            # 检查是否战斗失败
            found, _, _ = self.controller.find_image(template_name="combat_failure")
            if found:
                logger.warning("检测到战斗失败")
                success = False
                break
            
            # 检查是否有等级提升
            found, _, _ = self.controller.find_image(template_name="level_up")
            if found:
                logger.info("检测到等级提升")
                # 点击屏幕继续
                self.controller.tap(500, 500)
                time.sleep(1)
            
            # 等待一段时间再检查
            time.sleep(5)
        
        # 如果超时
        if time.time() - start_time >= timeout:
            logger.error("等待战斗结束超时")
            return False
        
        # 处理战斗结果
        self._handle_combat_result()
        
        return success
    
    def _handle_combat_result(self):
        """处理战斗结果界面"""
        logger.info("处理战斗结果界面...")
        
        # 点击屏幕跳过结算动画
        for _ in range(3):
            self.controller.tap(500, 500)
            time.sleep(1)
        
        # 点击确认结果按钮
        found, _, _ = self.controller.find_image(template_name="confirm_result")
        if found:
            self.controller.tap_image(template_name="confirm_result")
            time.sleep(2)
        logger.info("战斗结果处理完成")
    
    def check_auto_deploy(self):
        """
        检查并确保自动部署已开启
        
        Returns:
            bool: 自动部署是否已开启
        """
        logger.info("检查自动部署状态...")
        
        # 获取当前截图
        self.controller.take_screenshot()
        
        # 检查自动部署开关状态
        # 这里需要根据实际界面调整，可能需要检查开关的颜色或其他特征
        found, _, _ = self.controller.find_image(template_name="auto_deploy")
        
        if not found:
            logger.info("自动部署已开启")
            return True
        else:
            logger.warning("自动部署未开启，尝试开启...")
            # 点击自动部署开关位置
            # 这里需要根据实际界面调整坐标
            self.controller.tap_image(template_name="auto_deploy")
            time.sleep(1)
            
            # 再次检查
            self.controller.take_screenshot()
            found, _, _ = self.controller.find_image(template_name="auto_deploy")
            
            if found:
                logger.info("已成功开启自动部署")
                return True
            else:
                logger.error("无法开启自动部署")
                return False
    
    def return_to_main(self):
        """
        返回主界面
        
        Returns:
            bool: 是否成功返回主界面
        """
        logger.info("正在返回主界面...")
        
        # 点击返回按钮，可能需要点击多次
        for _ in range(4):
            if self.controller.tap_image(template_name="back_button"):
                time.sleep(2)
            else:
                break
        
        logger.info("已返回主界面")
        return True
    
    def execute_last_combat(self, use_sanity_item=False, max_times=1):
        """
        执行完整的上一次作战流程
        
        Args:
            use_sanity_item: 是否使用理智药剂，默认为False
            max_times: 最大作战次数，默认为1
            
        Returns:
            int: 成功完成的作战次数
        """
        logger.info(f"开始执行上一次作战流程，计划次数: {max_times}...")
        
        # 导航到作战界面
        if not self.navigate_to_combat():
            return 0
        # 开始上一次作战
        completed_times = self.start_last_combat(use_sanity_item, max_times)
        
        # 返回主界面
        self.return_to_main()
        
        logger.info(f"上一次作战流程执行完成，共完成 {completed_times}/{max_times} 次作战")
        return completed_times

# 测试代码
if __name__ == "__main__":
    # 创建作战模块实例
    combat = ArknightsCombat()
    
    # 连接到模拟器
    if combat.controller.connect_emulator():
        print("成功连接到模拟器")
        
        # 执行上一次作战流程
        completed = combat.execute_last_combat(use_sanity_item=True, max_times=3)
        print(f"共完成 {completed} 次作战")
    else:
        print("连接模拟器失败")
