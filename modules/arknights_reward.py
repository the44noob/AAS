#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
明日方舟领取奖励模块
负责执行领取各类奖励的操作
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
logger = logging.getLogger('ArknightsReward')

class ArknightsReward:
    """明日方舟奖励类，负责执行领取各类奖励的操作"""
    
    # 奖励相关界面元素模板
    TEMPLATES = {
        "mission_icon": "mission_icon.png",          # 主界面任务图标
        "daily_mission": "daily_mission.png",        # 日常任务标签
        "weekly_mission": "weekly_mission.png",      # 周常任务标签
        "collect_all": "collect_all_rewards.png",    # 全部领取按钮
        "confirm_collect": "confirm_collect.png",    # 确认领取按钮
        "mail_icon": "mail_icon.png",                # 主界面邮件图标
        "collect_mail": "collect_mail.png",          # 收取邮件按钮
        "collect_attachment": "collect_attachment.png", # 收取附件按钮
        "friend_icon": "friend_icon.png",            # 主界面好友图标
        "friend_credit": "friend_credit.png",        # 好友信用标签?
        "collect_credit": "collect_credit.png",      # 收取信用按钮
        "shop_icon": "shop_icon.png",                # 主界面商店图标
        "credit_shop": "credit_shop.png",            # 信用商店标签
        "buy_all": "buy_all.png",                    # 一键购买按钮
        "confirm_buy": "confirm_buy.png",            # 确认购买按钮
        "back_button": "back_button.png",            # 返回按钮
        "close_button": "close_button.png",          # 关闭按钮
        "notification": "notification.png",          # 通知图标（红点）?
    }
    
    def __init__(self, controller=None, template_dir=None):
        """
        初始化明日方舟奖励模块
        
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
        
        logger.info("明日方舟奖励模块初始化完成")
    
    def _load_templates(self):
        """加载奖励相关的模板图像"""
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
    
    def collect_daily_missions(self):
        """
        收集日常任务奖励
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始收集日常任务奖励...")
        
        # 点击任务图标
        if not self.controller.tap_image(template_name="mission_icon", max_retries=3):
            logger.error("未找到任务图标")
            return False
        
        # 等待任务界面加载
        time.sleep(2)
        
        # 确保选中日常任务标签
        self.controller.tap_image(template_name="daily_mission")
        time.sleep(1)
        
        # 点击全部领取按钮
        if not self.controller.tap_image(template_name="collect_all", max_retries=3):
            logger.warning("未找到全部领取按钮，可能没有可领取的日常任务奖励")
            # 返回主界面
            self.controller.tap_image(template_name="back_button")
            return True
        
        # 等待领取动画
        time.sleep(2)
        
        # 点击确认按钮（如果有）
        self.controller.tap_image(template_name="confirm_collect")
        time.sleep(1)
        
        # 返回主界面
        self.controller.tap_image(template_name="back_button")
        time.sleep(1)
        
        logger.info("日常任务奖励收集完成")
        return True
    
    def collect_weekly_missions(self):
        """
        收集周常任务奖励
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始收集周常任务奖励...")
        
        # 点击任务图标
        if not self.controller.tap_image(template_name="mission_icon", max_retries=3):
            logger.error("未找到任务图标")
            return False
        
        # 等待任务界面加载
        time.sleep(2)
        
        # 点击周常任务标签
        if not self.controller.tap_image(template_name="weekly_mission", max_retries=3):
            logger.error("未找到周常任务标签")
            # 返回主界面
            self.controller.tap_image(template_name="back_button")
            return False
        
        time.sleep(1)
        
        # 点击全部领取按钮
        if not self.controller.tap_image(template_name="collect_all", max_retries=3):
            logger.warning("未找到全部领取按钮，可能没有可领取的周常任务奖励")
            # 返回主界面
            self.controller.tap_image(template_name="back_button")
            return True
        
        # 等待领取动画
        time.sleep(2)
        
        # 点击确认按钮（如果有）
        self.controller.tap_image(template_name="confirm_collect")
        time.sleep(1)
        
        # 返回主界面
        self.controller.tap_image(template_name="back_button")
        time.sleep(1)
        
        logger.info("周常任务奖励收集完成")
        return True
    
    def collect_mail(self):
        """
        收集邮件奖励
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始收集邮件奖励...")
        
        # 检查是否有邮件通知
        self.controller.take_screenshot()
        found, _, _ = self.controller.find_image(template_name="notification", region=(700, 100, 200, 200))
        
        if not found:
            logger.info("没有新邮件通知，跳过邮件收集")
            return True
        
        # 点击邮件图标
        if not self.controller.tap_image(template_name="mail_icon", max_retries=3):
            logger.error("未找到邮件图标")
            return False
        
        # 等待邮件界面加载
        time.sleep(2)
        
        # 点击收取邮件按钮
        if not self.controller.tap_image(template_name="collect_mail", max_retries=3):
            logger.warning("未找到收取邮件按钮，可能没有可收取的邮件")
            # 返回主界面
            self.controller.tap_image(template_name="back_button")
            return True
        
        # 等待收取动画
        time.sleep(2)
        
        # 点击收取附件按钮（如果有）
        #self.controller.tap_image(template_name="collect_attachment")
        while not self.controller.find_image("mail.png"):
            self.controller.tap(958.5,964.0)
        time.sleep(1)
        
        # 返回主界面
        self.controller.tap_image(template_name="back_button")
        time.sleep(1)
        
        logger.info("邮件奖励收集完成")
        return True
    
    def collect_friend_credits(self):
        """
        收集好友信用
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始收集好友信用...")
        
        # 点击好友图标
        #if not self.controller.tap_image(template_name="friend_icon", max_retries=3):
        #    logger.error("未找到好友图标")
        #    return False
        
        ## 等待好友界面加载
        #time.sleep(2)
        
        if not self.controller.tap_image(template_name="shop_icon", max_retries=3):
            logger.error("未找到商店图标")
            return False
        time.sleep(2)
        if not self.controller.tap_image(template_name="credit_shop", max_retries=3):
            logger.error("未找到信用商店图标")
            return False
        time.sleep(2)
        
        # 点击收取信用按钮
        if not self.controller.tap_image(template_name="collect_credit", max_retries=3):
            logger.warning("未找到收取信用按钮，可能没有可收取的信用")
            # 返回主界面
            self.controller.tap_image(template_name="back_button")
            return True
        
        # 等待收取动画
        time.sleep(2)
        self.controller.tap_image(template_name="confirm_collect")
        # 返回主界面
        self.controller.tap_image(template_name="back_button")
        time.sleep(1)
        
        logger.info("好友信用收集完成")
        return True
    
    def buy_from_credit_shop(self):
        """
        在信用商店购买物品
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始在信用商店购买物品...")
        
        # 点击商店图标
        if not self.controller.tap_image(template_name="shop_icon", max_retries=3):
            logger.error("未找到商店图标")
            return False
        
        # 等待商店界面加载
        time.sleep(2)
        
        # 点击信用商店标签
        if not self.controller.tap_image(template_name="credit_shop", max_retries=3):
            logger.error("未找到信用商店标签")
            # 返回主界面
            self.controller.tap_image(template_name="back_button")
            return False
        
        time.sleep(1)

            
        # 等待购买确认弹窗
        time.sleep(1)
        position = [(190,393),(575,393),(956,393),(1336,393),(1720,393),(190,777),(575,777),(956,777),(1336,777),(1720,777)]
        for x,y in position:
            if self.controller.tap(x,y):
                time.sleep(1)
                # 点击确认购买按钮
                self.controller.tap(1393.3,873.2)
                time.sleep(5)
                if(self.controller.find_image("is_poor.png")):
                    self.controller.tap_image(template_name="back_button")
                self.controller.tap(958.5,964.0)

        # 返回主界面
        self.controller.tap_image(template_name="back_button")
        time.sleep(1)
        
        logger.info("信用商店购买完成")
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
            if self.controller.tap_image(template_name="back_button"):
                time.sleep(1)
            else:
                break
        
        logger.info("已返回主界面")
        return True
    
    def execute_reward_collection(self):
        """
        执行完整的奖励收集流程
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始执行奖励收集流程...")
        
        # 收集日常任务奖励
        self.collect_daily_missions()
        
        # 收集周常任务奖励
        self.collect_weekly_missions()
        
        # 收集邮件奖励
        self.collect_mail()
        
        # 收集好友信用
        self.collect_friend_credits()
        
        # 在信用商店购买物品
        self.buy_from_credit_shop()
        
        # 确保返回主界面
        self.return_to_main()
        
        logger.info("奖励收集流程执行完成")
        return True

# 测试代码
if __name__ == "__main__":
    # 创建奖励模块实例
    reward = ArknightsReward()
    
    # 连接到模拟器
    if reward.controller.connect_emulator():
        print("成功连接到模拟器")
        
        # 执行奖励收集流程
        if reward.execute_reward_collection():
            print("奖励收集流程执行成功")
        else:
            print("奖励收集流程执行失败")
    else:
        print("连接模拟器失败")
