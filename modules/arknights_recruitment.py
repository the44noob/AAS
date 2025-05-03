#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
明日方舟公开招募模块
负责执行公开招募相关操作
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
logger = logging.getLogger('ArknightsRecruitment')

class ArknightsRecruitment:
    """明日方舟公开招募类，负责执行公开招募相关操作"""
    
    # 公开招募相关界面元素模板
    TEMPLATES = {
        "recruitment_icon": "recruitment_icon.png",      # 主界面公开招募图标
        "recruit_now": "recruit_now.png",                # 立即招募按钮
        "confirm_recruit": "confirm_recruit.png",        # 确认招募按钮
        "skip_animation": "skip_animation.png",          # 跳过动画按钮
        "recruit_again": "recruit_again.png",            # 再次招募按钮？
        "refresh_tags": "refresh_tags.png",              # 刷新标签按钮
        "confirm_refresh": "confirm_refresh.png",        # 确认刷新按钮?
        "nine_hours": "nine_hours.png",                  # 9小时选项？
        "start_recruit": "start_recruit.png",            # 开始招募按钮
        "expedited_plan": "expedited_plan.png",          # 加急许可按钮
        "use_expedited": "use_expedited.png",            # 使用加急许可按钮
        "back_button": "back_button.png",                # 返回按钮
        "empty_slot": "empty_slot.png",                  # 空闲招募位
        "finished_slot": "finished_slot.png",            # 已完成招募位
        "select_operator": "select_operator.png",        # 选择干员按钮?
    }
    
    # 标签位置（相对于标签区域的坐标）
    TAG_POSITIONS = [
        (667.7, 573.5),  # 第一个标签位置
        (926.5, 573.5),  # 第二个标签位置
        (1166.4, 573.5),  # 第三个标签位置
        (667.7, 681.4),  # 第四个标签位置
        (926.5, 681.4),  # 第五个标签位置
    ]
    TAG_REGION = [
        (565, 543, 774, 606), #第一个标签区域
        (817, 543, 1027, 606), #第二个标签区域
        (1066, 543, 1277, 606), #第三个标签区域
        (565, 651, 776, 714), #第四个标签区域
        (817, 651, 1027, 714), #第五个标签区域
    ]
    tag_dic = {}
    # 高级标签排列
    TAG_ORDER = [
        #三标签
    ("防护", "群攻", "输出"),
    ("防护", "群攻", "生存"),
    ("防护", "群攻", "术师干员"),
    ("防护", "群攻", "近卫干员"),
    ("防护", "群攻", "位移"),
    ("防护", "输出", "生存"),
    ("防护", "输出", "术师干员"),
    ("防护", "输出", "近卫干员"),
    ("防护", "输出", "位移"),
    ("防护", "生存", "术师干员"),
    ("防护", "生存", "近卫干员"),
    ("防护", "生存", "位移"),
    ("防护", "术师干员", "近卫干员"),
    ("防护", "术师干员", "位移"),
    ("防护", "近卫干员", "位移"),
    ("重装干员", "输出", "生存"),
    ("重装干员", "输出", "位移"),
    ("重装干员", "生存", "位移"),
    ("医疗干员", "输出", "术师干员"),
    ("位移", "输出", "减速"),
        # 双标签
    ("控场", "先锋干员"), 
    ("控场", "特种干员"), 
    ("控场", "辅助干员"), 
    ("控场", "近战位"),
    ("爆发", "术师干员"), 
    ("爆发", "狙击干员"), 
    ("爆发", "远程位"),
    ("支援", "先锋干员"), 
    ("支援", "费用回复"), 
    ("支援", "辅助干员"), 
    ("支援", "生存"),
    ("削弱", "辅助干员"), 
    ("削弱", "特种干员"),
    ("召唤", "辅助干员"),
    ("特种干员", "减速"), 
    ("特种干员", "削弱"), 
    ("特种干员", "生存"),
    ("防护", "群攻"), 
    ("防护", "输出"), 
    ("防护", "生存"), 
    ("防护", "术师干员"), 
    ("防护", "近卫干员"), 
    ("防护", "位移"),
    ("重装干员", "输出"), 
    ("重装干员", "生存"), 
    ("重装干员", "位移"),
    ("医疗干员", "输出"), 
    ("医疗干员", "术师干员"),
    ("位移", "输出"), 
    ("位移", "减速"),
    ("远程位", "先锋干员"), 
    ("远程位", "费用回复"),
    ("生存", "狙击干员"), 
    ("生存", "远程位"),
    ("减速", "术师干员"), 
    ("减速", "狙击干员"), 
    ("减速", "群攻"), 
    ("减速", "近卫干员"), 
    ("减速", "近战位"), 
    ("减速", "输出"), 
    ("减速", "医疗干员"),
    ("医疗干员", "辅助干员"), 
    ("医疗干员", "先锋干员"), 
    ("医疗干员", "费用回复"),
        # 单标签
    ("高级资深干员"),
    ("资深干员"),
    ("特种干员"),
    ("控场"),
    ("爆发"),
    ("支援"),
    ("削弱"),
    ("快速复活"),
    ("位移"),
    ("召唤"),

    ]
    
    def __init__(self, controller=None, template_dir=None):
        """
        初始化明日方舟公开招募模块
        
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
        
        logger.info("明日方舟公开招募模块初始化完成")

    def _load_templates(self):
        """加载公开招募相关的模板图像"""
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
    def find_first_matching_tag_combination(self):
        """
        根据 TAG_ORDER 查找 tag_dic 中包含的第一个完整组合

        Returns:
            tuple or None: 第一个匹配的标签组合，若无匹配则返回 None
        """
        for combination in self.TAG_ORDER:
            if all(tag in self.tag_dic for tag in combination):
                logger.info(f"找到匹配的标签组合: {combination}")
                return combination
        logger.info("未找到任何匹配的标签组合")
        return None
    def navigate_to_recruitment(self):
        """
        导航到公开招募界面
        
        Returns:
            bool: 是否成功导航到公开招募界面
        """
        logger.info("正在导航到公开招募界面...")
        
        # 确保在主界面
        # 可以添加检查主界面的代码，如果不在主界面则返回主界面
        
        # 点击公开招募图标
        if not self.controller.tap_image(template_name="recruitment_icon", max_retries=3):
            logger.error("未找到公开招募图标")
            return False
        
        # 等待公开招募界面加载
        time.sleep(2)
        
        # 检查是否成功进入公开招募界面
        self.controller.take_screenshot()
        found, _, _ = self.controller.find_image(template_name="recruit_now")
        
        if found:
            logger.info("已成功进入公开招募界面")
            return True
        else:
            logger.error("导航到公开招募界面失败")
            return False
    
    def check_recruitment_slots(self):
        """
        检查招募槽位状态
        
        Returns:
            tuple: (空闲槽位列表, 已完成槽位列表)
        """
        logger.info("正在检查招募槽位状态...")
        
        # 获取当前截图
        self.controller.take_screenshot()
        
        # 查找所有空闲槽位
        empty_slots = self.controller.find_all_images(image = self.controller.screenshot_path,template_name="empty_slot")
        empty_positions = [pos for pos, _ in empty_slots]
        
        # 查找所有已完成槽位
        finished_slots = self.controller.find_all_images(image = self.controller.screenshot_path,template_name="finished_slot")
        finished_positions = [pos for pos, _ in finished_slots]
        
        logger.info(f"找到 {len(empty_positions)} 个空闲槽位, {len(finished_positions)} 个已完成槽位")
        return empty_positions, finished_positions
    
    def collect_finished_recruitment(self, positions):
        """
        收取已完成的招募结果
        
        Args:
            positions: 已完成槽位的位置列表
            
        Returns:
            int: 成功收取的数量
        """
        if not positions:
            logger.info("没有已完成的招募可收取")
            return 0
        
        logger.info(f"开始收取 {len(positions)} 个已完成的招募...")
        collected = 0
        
        for pos in positions:
            # 点击已完成的槽位
            if self.controller.tap(pos[0], pos[1]):
                # 等待动画
                time.sleep(1)
              
                # 尝试跳过动画
                self.controller.tap_image(template_name="skip_animation")
                time.sleep(2)
                
                # 点击屏幕任意位置继续
                self.controller.tap(500, 500)
                time.sleep(1)
                
                collected += 1
                logger.info(f"已收取第 {collected} 个招募结果")
            
            # 等待界面恢复
            time.sleep(2)
        
        logger.info(f"成功收取 {collected} 个招募结果")
        return collected
    
    def start_new_recruitment(self, positions, use_expedited=False, select_tags=True, set_time=True):
        """
        开始新的招募
        
        Args:
            positions: 空闲槽位的位置列表
            use_expedited: 是否使用加急许可，默认为False
            select_tags: 是否选择标签，默认为True
            set_time: 是否设置时间为9小时，默认为True
            
        Returns:
            int: 成功开始的招募数量
        """
        if not positions:
            logger.info("没有空闲槽位可用于招募")
            return 0
        
        logger.info(f"开始在 {len(positions)} 个空闲槽位中进行招募...")
        started = 0
        
        for pos in positions:
            # 点击空闲槽位
            if self.controller.tap(pos[0], pos[1]):
                # 等待界面加载
                time.sleep(1)
                
                # 如果需要选择标签
                if select_tags:
                    self._select_tags()
                
                # 如果需要设置时间为9小时
                if set_time:
                    if not self.controller.tap(677.5,451.6):
                        logger.warning("未找到9小时选项")
                
                # 点击开始招募按钮
                if self.controller.tap_image(template_name="start_recruit"):
                    # 等待确认界面
                    time.sleep(1)
                    
                    # 点击确认招募按钮
                    started += 1
                    logger.info(f"已开始第 {started} 个招募")
                    
                    # 如果需要使用加急许可
                    if use_expedited:
                        time.sleep(1)
                        if self.controller.tap_image(template_name="expedited_plan"):
                            time.sleep(1)
                            self.controller.tap_image(template_name="use_expedited")
                            logger.info("已使用加急许可")
                
                # 等待界面恢复
                time.sleep(2)
        
        logger.info(f"成功开始 {started} 个招募")
        return started
    
    def _select_tags(self, num_tags=1):
        """
        选择招募标签
        
        Args:
            num_tags: 要选择的标签数量，默认为1
            
        Returns:
            bool: 是否成功选择标签
        """
        logger.info(f"正在选择 {num_tags} 个招募标签...")
        
        # 确保标签数量合法
        num_tags = min(max(1, num_tags), 3)
        
        ## 随机选择标签
        #selected_indices = random.sample(range(len(self.TAG_POSITIONS)), num_tags)
        #
        #for idx in selected_indices:
        #    pos = self.TAG_POSITIONS[idx]
        #    self.controller.tap(pos[0], pos[1])
        #    time.sleep(0.5)
        #
        #logger.info(f"已选择 {num_tags} 个招募标签")
        index = 0
        self.controller.take_screenshot()
        for region in self.TAG_REGION:
            extract_text = self.controller.recognizer.extract_text_from_region(self.controller.screenshot_path,region_coords = region,lang='chi_sim')
            self.tag_dic[extract_text] = self.TAG_POSITIONS[index]
            logger.info(f"第{index+1}个标签名为 {extract_text} ，位置是 {self.TAG_POSITIONS[index]}")
            index += 1
        combination = self.find_first_matching_tag_combination()

        if combination:
            logger.info(f"使用标签组合: {combination}")
            for tag in combination:
                self.controller.tap(self.tag_dic[tag][0], self.tag_dic[tag][1])
                time.sleep(0.5)
        else:
            logger.warning("未找到可用的高级招募组合，将使用默认逻辑选择标签")
            # 随机选择标签
            selected_indices = random.sample(range(len(self.TAG_POSITIONS)), num_tags)
            
            for idx in selected_indices:
                pos = self.TAG_POSITIONS[idx]
                self.controller.tap(pos[0], pos[1])
                time.sleep(0.5)           
            logger.info(f"已选择 {num_tags} 个招募标签")
        return True
    
    def refresh_tags(self):
        """
        刷新招募标签
        
        Returns:
            bool: 是否成功刷新标签
        """
        logger.info("正在刷新招募标签...")
        
        # 点击刷新标签按钮
        if not self.controller.tap_image(template_name="refresh_tags"):
            logger.error("未找到刷新标签按钮")
            return False
        
        # 等待确认界面
        time.sleep(1)
        
        # 点击确认刷新按钮
        if not self.controller.tap_image(template_name="confirm_refresh"):
            logger.error("未找到确认刷新按钮")
            return False
        
        # 等待刷新完成
        time.sleep(2)
        
        logger.info("已成功刷新招募标签")
        return True
    
    def return_to_main(self):
        """
        返回主界面
        
        Returns:
            bool: 是否成功返回主界面
        """
        logger.info("正在返回主界面...")
        
        # 点击返回按钮
        if not self.controller.tap_image(template_name="back_button", max_retries=3):
            logger.error("未找到返回按钮")
            return False
        
        # 等待主界面加载
        time.sleep(2)
        
        logger.info("已返回主界面")
        return True
    
    def execute_recruitment(self, collect_finished=True, start_new=True, use_expedited=False):
        """
        执行完整的公开招募流程
        
        Args:
            collect_finished: 是否收取已完成的招募，默认为True
            start_new: 是否开始新的招募，默认为True
            use_expedited: 是否使用加急许可，默认为False
            
        Returns:
            bool: 操作是否成功
        """
        logger.info("开始执行公开招募流程...")
        
        # 导航到公开招募界面
        if not self.navigate_to_recruitment():
            return False
        
        # 检查招募槽位状态
        empty_positions, finished_positions = self.check_recruitment_slots()
        
        # 收取已完成的招募
        if collect_finished and finished_positions:
            self.collect_finished_recruitment(finished_positions)
            
            # 重新检查槽位状态
            empty_positions, _ = self.check_recruitment_slots()
        
        # 开始新的招募
        if start_new and empty_positions:
            self.start_new_recruitment(empty_positions, use_expedited)
        
        # 返回主界面
        self.return_to_main()
        
        logger.info("公开招募流程执行完成")
        return True

# 测试代码
if __name__ == "__main__":
    # 创建公开招募模块实例
    recruitment = ArknightsRecruitment()
    
    # 连接到模拟器
    if recruitment.controller.connect_emulator():
        print("成功连接到模拟器")
        
        # 执行公开招募流程
        if recruitment.execute_recruitment():
            print("公开招募流程执行成功")
        else:
            print("公开招募流程执行失败")
    else:
        print("连接模拟器失败")
